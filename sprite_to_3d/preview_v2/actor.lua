-- Actor Class for 3D Previewer
-- Handles Skeleton construction, Animation playback, and Model-to-Bone syncing.
-- Rigorously annotated for coordinate systems and Menori integration.

local menori = require("menori")
local ml = menori.ml
local vec3 = ml.vec3
local quat = ml.quat
local json = require("json")

local Actor = {}
Actor.__index = Actor

--- Constructor for the Actor
-- @param rig_path Path to the rig.json file
-- @param assets_base_path Directory containing the GLTF parts
-- @param shader The shader to use for rendering models
-- @param palette The palette texture to use for models
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
	self.bones = {} -- Bone nodes (hierarchical)
	self.bone_models = {} -- Model nodes (flat, synced to bones)
	self.bind_world_rotations = {} -- Used for relative rotation calculation
	self.animations = {}
	self.active_anim_idx = 0
	self.time = 0

	-- Pre-allocate temp objects to avoid GC pressure
	self.temp_pos = vec3()
	self.temp_rot = quat()
	self.temp_scale = vec3()

	-- Load Rig
	local rig_content = love.filesystem.read(rig_path)
	if rig_content then
		self.rig_data = json.decode(rig_content)
		self:_build_skeleton()
	else
		error("Failed to load rig: " .. rig_path)
	end

	return self
end

local function ensure_16(d)
	if not d then return nil end
	local out = {}
	for i = 1, 16 do
		out[i] = d[i] or (i == 16 and 1 or 0)
	end
	return out
end

--- Internal: Builds the bone hierarchy and loads associated models
function Actor:_build_skeleton()
	local rest_pose = self.rig_data.skeleton.rest_pose
	local topology = self.rig_data.skeleton.topology
	local bind_matrices = self.rig_data.skeleton.bind_matrices
	local bone_scales = self.rig_data.skeleton.bone_scales or {}

	-- 1. Create all Bone Nodes
	-- Bones are kept in a separate hierarchy (self.skeleton_root)
	for bone_name, _ in pairs(rest_pose) do
		self.bones[bone_name] = menori.Node(bone_name)
	end

	-- 2. Link Nodes & Set Bind Pose
	-- COORDINATE NOTE: The matrices in JSON are Row-Major. 
	-- Menori matrices are Column-Major. We must transpose/re-order when loading.
	for bone_name, parent_name in pairs(topology) do
		local node = self.bones[bone_name]
		
		-- Parent-Child linkage
		if parent_name and self.bones[parent_name] then
			self.bones[parent_name]:attach(node)
		else
			self.skeleton_root:attach(node)
		end

		if bind_matrices and bind_matrices[bone_name] then
			local d = bind_matrices[bone_name]
			-- Transpose Row-Major to Column-Major
			local m = ml.mat4(ensure_16({
				d[1], d[5], d[9], d[13],
				d[2], d[6], d[10], d[14],
				d[3], d[7], d[11], d[15],
				d[4], d[8], d[12], d[16],
			}))
			m:decompose(self.temp_pos, self.temp_rot, self.temp_scale)

			node:set_position(self.temp_pos:clone())
			node:set_rotation(self.temp_rot:clone())
			
			-- Use custom scale if provided, otherwise use decomposed bind scale
			local s = bone_scales[bone_name]
			if s then
				node:set_scale(vec3(s[1], s[2], s[3]))
			else
				node:set_scale(self.temp_scale:clone())
			end
		end

		-- Load the 3D model part for this bone if it exists
		self:_load_bone_model(bone_name)
	end

	-- 3. Capture World Bind Rotations
	-- We need these because our modular models (limbs/head) are exported in their own local T-pose.
	-- When syncing, we don't just copy the bone rotation; we apply the rotation *relative* to the bind pose.
	-- Model_Rotation = Bone_Current_World_Rotation * Inverse(Bone_Bind_World_Rotation)
	self.root:recursive_update_transform()
	for bone_name, node in pairs(self.bones) do
		self.bind_world_rotations[bone_name] = node:get_world_rotation()
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
		-- IMPORTANT: Models are attached to a FLAT mesh_root. 
		-- We do NOT parent models to bones because we want to avoid 
		-- non-uniform scale inheritance issues and simplify the hierarchy.
		self.mesh_root:attach(scene_nodes[1])
		self.bone_models[bone_name] = scene_nodes[1]
	end
end

--- Loads all animations from a directory
-- @param dir_path Directory containing .json animation files
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
-- @param dt Delta time
-- @param anim_speed Playback speed in frames per second
function Actor:update(dt, anim_speed)
	self.time = self.time + dt
	
	-- 1. Apply Animation to Bones
	local anim = self.animations[self.active_anim_idx]
	if anim and anim.data.frames then
		local frames = anim.data.frames
		local frame_idx = math.floor(self.time * anim_speed) % #frames
		local frame = frames[frame_idx + 1]

		for bone_name, d in pairs(frame) do
			local bone = self.bones[bone_name]
			if bone then
				-- Convert Row-Major to Column-Major
				local m = ml.mat4(ensure_16({
					d[1], d[5], d[9], d[13],
					d[2], d[6], d[10], d[14],
					d[3], d[7], d[11], d[15],
					d[4], d[8], d[12], d[16],
				}))
				m:decompose(self.temp_pos, self.temp_rot, self.temp_scale)

				bone:set_position(self.temp_pos:clone())
				bone:set_rotation(self.temp_rot:clone())
				bone:set_scale(self.temp_scale:clone())
			end
		end
	end

	-- 2. Propagate bone transforms down the hierarchy
	self.skeleton_root:recursive_update_transform()

	-- 3. Sync Flat Models to Bones
	-- This is the "Skinning" replacement. Instead of GPU skinning, we manually
	-- position/rotate each modular part to match its corresponding bone.
	for name, model in pairs(self.bone_models) do
		local bone = self.bones[name]
		if bone then
			-- Copy World Position directly
			model:set_position(bone:get_world_position())
			
			-- Apply Relative Rotation:
			-- The model's local 'up' should match the bone's current 'up' relative to bind.
			local bind_world_rot = self.bind_world_rotations[name]
			if bind_world_rot then
				-- New_World = Animated_Bone_World * Inverse(Bind_Bone_World)
				model:set_rotation(bone:get_world_rotation() * bind_world_rot:inverse())
			else
				model:set_rotation(bone:get_world_rotation())
			end

			-- Copy World Scale
			model:set_scale(bone:get_world_scale())
		end
	end

	-- 4. Propagate model transforms
	self.mesh_root:recursive_update_transform()
end

--- Draws the skeleton for debugging
-- @param camera The menori Camera3D used for screen-space projection
-- @param view_rect The {x, y, w, h} viewport rectangle
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
-- @param color {r, g, b, a} table
-- @param bone_colors Optional table mapping bone_name -> color
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
