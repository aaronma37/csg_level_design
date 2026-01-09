-- Actor Class for 3D Previewer
-- Handles Skeleton construction, Animation playback, and Model-to-Bone syncing.
-- Optimized for stability with non-uniform scaling and fluid interpolation.

local menori = require("menori")
local ml = menori.ml
local vec3 = ml.vec3
local quat = ml.quat
local json = require("json")

local Actor = {}
Actor.__index = Actor

local function ensure_16(d)
	if not d then return nil end
	local out = {}
	for i = 1, 16 do
		out[i] = d[i] or (i == 16 and 1 or 0)
	end
	return out
end

--- Constructor for the Actor
function Actor.new(rig_path, assets_base_path, shader, palette)
	local self = setmetatable({}, Actor)

	self.assets_path = assets_base_path
	self.shader = shader
	self.palette = palette

	-- Scene Graph Nodes
	self.root = menori.Node("ActorRoot")
	self.skeleton_root = menori.Node("SkeletonRoot")
	self.mesh_root = menori.Node("MeshRoot")
	self.root:attach(self.skeleton_root)
	self.root:attach(self.mesh_root)

	-- State
	self.bones = {} 
	self.bone_models = {} 
	self.bind_world_rotations = {} 
	self.animations = {}
	self.active_anim_idx = 0
	self.time = 0

	-- Pre-allocate temp objects for high-performance updates
	self.temp_pos = vec3()
	self.temp_rot = quat()
	self.temp_scale = vec3()
	
	self.interp_p1 = vec3()
	self.interp_r1 = quat()
	self.interp_p2 = vec3()
	self.interp_r2 = quat()

	-- Load Rig
	local rig_content = love.filesystem.read(rig_path)
	if rig_content then
		self.rig_data = json.decode(rig_content)
		self.global_scale = (self.rig_data.height or 50) / 50.0
		self:_build_skeleton()
	else
		error("Failed to load rig: " .. rig_path)
	end

	return self
end

--- Internal: Builds the bone hierarchy and loads associated models
function Actor:_build_skeleton()
	local rest_pose = self.rig_data.skeleton.rest_pose
	local topology = self.rig_data.skeleton.topology
	local bind_matrices = self.rig_data.skeleton.bind_matrices
	local bone_scales = self.rig_data.skeleton.bone_scales or {}
	local gs = self.global_scale or 1.0

	-- 1. Create all Bone Nodes (Unscaled for rotation stability)
	for bone_name, _ in pairs(rest_pose) do
		self.bones[bone_name] = menori.Node(bone_name)
	end

	-- 2. Link Nodes & Set Bind Pose
	for bone_name, parent_name in pairs(topology) do
		local node = self.bones[bone_name]
		if parent_name and self.bones[parent_name] then
			self.bones[parent_name]:attach(node)
		else
			self.skeleton_root:attach(node)
		end

		if bind_matrices and bind_matrices[bone_name] then
			local d = bind_matrices[bone_name]
			local m = ml.mat4(ensure_16({
				d[1], d[5], d[9], d[13],
				d[2], d[6], d[10], d[14],
				d[3], d[7], d[11], d[15],
				d[4], d[8], d[12], d[16],
			}))
			m:decompose(self.temp_pos, self.temp_rot, self.temp_scale)

			-- SCALE STABILITY FIX:
			-- We scale the local position to match proportions, but we keep the bone 
			-- node's own scale at 1,1,1. This prevents Menori from encountering 
			-- singularities during world-matrix decomposition.
			local ps = bone_scales[parent_name] or {1, 1, 1}
			node:set_position(vec3(self.temp_pos.x * ps[1] * gs, self.temp_pos.y * ps[2] * gs, self.temp_pos.z * ps[3] * gs))
			node:set_rotation(self.temp_rot:clone())
			node:set_scale(vec3(1, 1, 1)) -- Keep internal scale uniform
		end

		self:_load_bone_model(bone_name)
	end

	-- 3. Capture WORLD bind rotations (MUST CLONE)
	-- Since bones are now unscaled (1,1,1), these rotations are perfectly stable.
	self.root:recursive_update_transform(true)
	for bone_name, node in pairs(self.bones) do
		self.bind_world_rotations[bone_name] = node:get_world_rotation():clone()
	end
end

--- Internal: Maps bone names to GLTF filenames and loads them
function Actor:_load_bone_model(bone_name)
	local map = {
		mixamorig_Hips = "base_pelvis",
		mixamorig_Spine = "base_spine",
		mixamorig_Spine1 = "base_spine1",
		mixamorig_Spine2 = "base_spine2",
		mixamorig_Head = "base_head",
		mixamorig_LeftShoulder = "base_leftshoulder",
		mixamorig_RightShoulder = "base_rightshoulder",
		mixamorig_LeftArm = "base_arm_l",
		mixamorig_RightArm = "base_arm_r",
		mixamorig_LeftForeArm = "base_elbow_l",
		mixamorig_RightForeArm = "base_elbow_r",
		mixamorig_LeftHand = "base_hand_l",
		mixamorig_RightHand = "base_hand_r",
		mixamorig_LeftUpLeg = "base_thigh_l",
		mixamorig_RightUpLeg = "base_thigh_r",
		mixamorig_LeftLeg = "base_knee_l",
		mixamorig_RightLeg = "base_knee_r",
		mixamorig_LeftFoot = "base_foot_l",
		mixamorig_RightFoot = "base_foot_r",
	}
	
	local filename = map[bone_name]
	if not filename then return end

	local path = self.assets_path .. "/" .. filename .. ".gltf"
	if not love.filesystem.getInfo(path) then return end

	local gltf_data = menori.glTFLoader.load(path)
	local scene_nodes = menori.NodeTreeBuilder.create(gltf_data, function(scene, builder)
		scene:traverse(function(n)
			if n.is_model_node then
				n.material.main_texture = self.palette
				n.material:set_shader(self.shader)
				n.material:set("unlit", true)
				n.material.mesh_cull_mode = "none"
			end
		end)
	end)

	if scene_nodes[1] then
		self.mesh_root:attach(scene_nodes[1])
		self.bone_models[bone_name] = scene_nodes[1]
	end
end

--- Loads all animations from a directory
function Actor:load_animations(dir_path)
	local files = love.filesystem.getDirectoryItems(dir_path)
	for _, file in ipairs(files) do
		if file:match("%.json$") and file ~= "rig.json" then
			local content = love.filesystem.read(dir_path .. "/" .. file)
			if content then
				local data = json.decode(content)
				local name = file:gsub("%.json$", ""):gsub("^%l", string.upper):gsub("_%l", string.upper):gsub("_", " ")
				table.insert(self.animations, { name = name, data = data })
			end
		end
	end
	table.sort(self.animations, function(a, b) return a.name < b.name end)
	if #self.animations > 0 then self.active_anim_idx = 1 end
end

--- Updates the actor state, animation, and syncs models
function Actor:update(dt, anim_speed)
	local anim = self.animations[self.active_anim_idx]
	local duration = 1.0
	local frame_count = 0
	if anim and anim.data.frames then
		frame_count = #anim.data.frames
		duration = frame_count / anim_speed
	end

	self.time = self.time + dt
	if self.time >= duration then
		self.time = self.time % duration
	end
	
	local topology = self.rig_data.skeleton.topology
	local bone_scales = self.rig_data.skeleton.bone_scales or {}
	local gs = self.global_scale or 1.0

	-- 1. Apply Animation to Bones with Interpolation
	if anim and frame_count > 1 then
		local float_frame = (self.time * anim_speed)
		local idx1 = math.floor(float_frame) % frame_count
		local idx2 = (idx1 + 1) % frame_count
		local alpha = float_frame - math.floor(float_frame)

		local frame1 = anim.data.frames[idx1 + 1]
		local frame2 = anim.data.frames[idx2 + 1]

		for bone_name, d1 in pairs(frame1) do
			local bone = self.bones[bone_name]
			local d2 = frame2[bone_name]
			if bone and d2 then
				-- Frame 1 Decomp
				local m1 = ml.mat4(ensure_16({
					d1[1], d1[5], d1[9], d1[13], d1[2], d1[6], d1[10], d1[14],
					d1[3], d1[7], d1[11], d1[15], d1[4], d1[8], d1[12], d1[16],
				}))
				m1:decompose(self.interp_p1, self.interp_r1)

				-- Frame 2 Decomp
				local m2 = ml.mat4(ensure_16({
					d2[1], d2[5], d2[9], d2[13], d2[2], d2[6], d2[10], d2[14],
					d2[3], d2[7], d2[11], d2[15], d2[4], d2[8], d2[12], d2[16],
				}))
				m2:decompose(self.interp_p2, self.interp_r2)

				-- Interpolate
				local p_interp = vec3.lerp(self.interp_p1, self.interp_p2, alpha)
				local r_interp = quat.slerp(self.interp_r1, self.interp_r2, alpha)
				r_interp:normalize()

				-- Apply proporational translation
				local ps = bone_scales[topology[bone_name]] or {1, 1, 1}
				bone:set_position(vec3(p_interp.x * ps[1] * gs, p_interp.y * ps[2] * gs, p_interp.z * ps[3] * gs))
				bone:set_rotation(r_interp)
			end
		end
	end

	-- 2. Propagate bone transforms
	self.skeleton_root:recursive_update_transform(true)

	-- 3. Sync Flat Models to Bones
	for name, model in pairs(self.bone_models) do
		local bone = self.bones[name]
		if bone then
			-- Sync World Position
			model:set_position(bone:get_world_position():clone())
			
			-- Sync Stable World Rotation
			local bind_world_rot = self.bind_world_rotations[name]
			if bind_world_rot then
				local current_world_rot = bone:get_world_rotation():clone()
				local rot = current_world_rot * bind_world_rot:inverse()
				rot:normalize()
				model:set_rotation(rot)
			else
				model:set_rotation(bone:get_world_rotation():clone())
			end

			-- Apply Model-Specific Scale directly to the mesh node
			local s = bone_scales[name]
			if s then
				model:set_scale(vec3(s[1], s[2], s[3]))
			else
				model:set_scale(vec3(1, 1, 1))
			end
		end
	end

	-- 4. Propagate model transforms
	self.mesh_root:recursive_update_transform(true)
end

--- Draws the skeleton for debugging
function Actor:draw_skeleton(camera, view_rect)
	love.graphics.setShader()
	love.graphics.setDepthMode("always", false)
	love.graphics.setColor(1, 1, 0, 1)

	for _, bone in pairs(self.bones) do
		local p1 = bone:get_world_position()
		local s1 = camera:world_to_screen_point(p1, view_rect)

		if s1.x > -50 and s1.x < view_rect[3] + 50 then
			love.graphics.circle("fill", s1.x, s1.y, 2)

			if bone.parent and self.bones[bone.parent.name] then
				local p2 = bone.parent:get_world_position()
				local s2 = camera:world_to_screen_point(p2, view_rect)
				love.graphics.line(s1.x, s1.y, s2.x, s2.y)
			end
		end
	end
	love.graphics.setColor(1, 1, 1, 1)
end

--- Sets a uniform color for all model parts
function Actor:set_model_colors(color, bone_colors)
	for name, model in pairs(self.bone_models) do
		local final_color = (bone_colors and bone_colors[name]) or color
		model:traverse(function(node)
			if node.is_model_node then
				node.material:set("baseColor", final_color)
			end
		end)
	end
end

function Actor:next_animation()
	if #self.animations > 0 then
		self.active_anim_idx = (self.active_anim_idx % #self.animations) + 1
		self.time = 0
	end
end

function Actor:get_active_animation_name()
	local anim = self.animations[self.active_anim_idx]
	return anim and anim.name or "None"
end

return Actor
