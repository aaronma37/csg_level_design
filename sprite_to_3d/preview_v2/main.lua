io.stdout:setvbuf("no")
local menori = require("menori")
local json = require("json")
local ml = menori.ml
local vec3 = ml.vec3
local quat = ml.quat

local HEAD_PATH = "assets/hero/base_head.gltf" -- Removed? No, I need to keep this concept but generic.
local RIG_PATH = "assets/hero/rig.json"
local ANIM_PATH = "assets/hero/walk.json"

local App = {
	time = 0,
	animation_speed = 24,

	-- Camera Params
	cam_angle = math.pi / 4,
	cam_dist = 100,
	cam_height = 20,
	cam_center = vec3(0, 25, 0),

	-- Skin Tint
	skin_tint = { 1.0, 0.7, 0.7 },
	skin_tint_strength = 1.0,

	show_skeleton = true,
	show_mesh = true,
}

function App:get_model_path(bone_name)
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
	local name = map[bone_name]
	if name then
		return "assets/hero/" .. name .. ".gltf"
	end
	return nil
end

function App:load_bone_model(bone_name)
	local path = self:get_model_path(bone_name)
	if not path then
		return
	end

	if love.filesystem.getInfo(path) then
		print("Loading: " .. path)
		local gltf_data = menori.glTFLoader.load(path)
		local scene_nodes = menori.NodeTreeBuilder.create(gltf_data, function(scene, builder)
			scene:traverse(function(n)
				if n.is_model_node then
					print("  Found model node: " .. (n.name or "unnamed"))
					n.material.main_texture = self.palette
					n.material:set_shader(self.shader)
					n.material:set("unlit", true)
					n.material:set("baseColor", { 1, 1, 1, 1 })
					n.material.mesh_cull_mode = "none"
				end
			end)
		end)

		if scene_nodes[1] then
			self.bones[bone_name]:attach(scene_nodes[1])
			scene_nodes[1]:set_position(vec3(0, 0, 0))

			-- Debug Cube Attachment
			local debug_node = menori.ModelNode(self.debug_mesh, self.debug_mat)
			debug_node:set_scale(vec3(4, 4, 4)) -- 4x4x4 cube
			self.bones[bone_name]:attach(debug_node)
		end
	end
end

function App:load()
	love.graphics.setDefaultFilter("nearest", "nearest")

	-- 1. Load Custom Shader
	local status, shader_or_err = pcall(love.graphics.newShader, "shaders/lighting.glsl")
	if status then
		self.shader = shader_or_err
	else
		print("Shader Error:", shader_or_err)
		self.shader = love.graphics.newShader([[
			vec4 effect(vec4 color, Image tex, vec2 texture_coords, vec2 screen_coords) {
				return Texel(tex, texture_coords) * color;
			}
		]])
	end

	self.palette = love.graphics.newImage("assets/hero/palette_texture.png")

	-- Debug Cube
	self.debug_mesh = menori.Box(1, 1, 1)
	self.debug_mat = menori.Material()
	self.debug_mat:set("baseColor", { 1, 0, 0, 1 })
	self.debug_mat:set("unlit", true)
	self.debug_mat:set_shader(self.shader)

	-- 2. Scene Setup
	self.scene = menori.Scene()
	self.root = menori.Node("scene_root")
	self.env = menori.Environment(nil)

	-- Root Debug Cube (Landmark)
	-- local root_cube = menori.ModelNode(self.debug_mesh, self.debug_mat)
	-- root_cube:set_position(vec3(0, 30, 0))
	-- root_cube:set_scale(vec3(5, 5, 5))
	-- self.root:attach(root_cube)

	-- Lighting
	self.env:set("ambientColor", { 0.2, 0.2, 0.25 })
	self.env:set("ambientIntensity", 1.0)
	self.env:set("dirLightDirection", { -0.6, -0.8, 0.5 })
	self.env:set("dirLightColor", { 1.5, 1.5, 1.4 })

	-- 3. Load Rig
	local rig_content, _ = love.filesystem.read(RIG_PATH)
	if rig_content then
		self.rig_data = json.decode(rig_content)
		print("Loaded Rig: " .. RIG_PATH)
		self:build_skeleton()
	else
		print("FAILED TO LOAD RIG: " .. RIG_PATH)
	end

	-- 3.5 Load Animation
	local anim_content, _ = love.filesystem.read(ANIM_PATH)
	if anim_content then
		self.anim_data = json.decode(anim_content)
		print("Loaded Animation: " .. ANIM_PATH .. " | Frames: " .. tostring(#self.anim_data.frames))
	else
		print("FAILED TO LOAD ANIMATION: " .. ANIM_PATH)
	end

	-- 4. View Setup
	local win_w, win_h = love.graphics.getDimensions()
	self.view_w, self.view_h = math.floor(win_w / 2), math.floor(win_h / 2)

	self.views = {}
	for i = 1, 4 do
		self.views[i] = {
			canvas = love.graphics.newCanvas(self.view_w, self.view_h),
			depth = love.graphics.newCanvas(self.view_w, self.view_h, { format = "depth24" }),
			camera = menori.Camera3D((i <= 2) and "ortho" or "perspective", { fov = 40, ortho_size = 5 }),
		}
	end

	self.temp_pos = vec3()
	self.temp_rot = quat()
	self.temp_scale = vec3()
end

function App:apply_animation(dt)
	if not self.anim_data or not self.bones then
		return
	end

	local frame_count = #self.anim_data.frames
	if frame_count == 0 then
		return
	end

	local current_frame_idx = math.floor(self.time * self.animation_speed) % frame_count
	local frame = self.anim_data.frames[current_frame_idx + 1]

	local debug_frame = (math.floor(self.time * 60) % 60 == 0)

	for bone_name, matrix_data in pairs(frame) do
		local bone = self.bones[bone_name]
		if bone then
			local d = matrix_data
			-- Convert Row-Major (JSON) to Column-Major (Menori)
			-- JSON: m00 m01 m02 tx ...
			-- Menori: m00 m10 m20 0 ...

			local m = ml.mat4({
				d[1],
				d[5],
				d[9],
				d[13],
				d[2],
				d[6],
				d[10],
				d[14],
				d[3],
				d[7],
				d[11],
				d[15],
				d[4],
				d[8],
				d[12],
				d[16],
			})

			m:decompose(self.temp_pos, self.temp_rot, self.temp_scale)

			if debug_frame and (bone_name == "mixamorig_Hips" or bone_name == "mixamorig_Head") then
				print(
					string.format("  Scale: %.2f, %.2f, %.2f", self.temp_scale.x, self.temp_scale.y, self.temp_scale.z)
				)
			end

			bone:set_position(self.temp_pos)
			bone:set_rotation(self.temp_rot)
			bone:set_scale(self.temp_scale)
		end
	end

	self.root:recursive_update_transform()
end

function App:build_skeleton()
	if not self.rig_data then
		return
	end

	self.bones = {}
	self.char_root = menori.Node("CharacterRoot")
	self.root:attach(self.char_root)

	-- Debug Cube on Char Root
	-- local char_debug = menori.ModelNode(self.debug_mesh, self.debug_mat)
	-- char_debug:set_scale(vec3(3, 3, 3))
	-- self.char_root:attach(char_debug)

	local rest_pose = self.rig_data.skeleton.rest_pose
	local topology = self.rig_data.skeleton.topology

	-- Create Nodes
	for bone_name, _ in pairs(rest_pose) do
		self.bones[bone_name] = menori.Node(bone_name)
		self.bones[bone_name].name = bone_name

		if bone_name == "mixamorig_Hips" then
			local hip_debug = menori.ModelNode(self.debug_mesh, self.debug_mat)
			hip_debug:set_scale(vec3(4, 4, 4))
			self.bones[bone_name]:attach(hip_debug)
		end
	end

	-- Link Nodes & Set Rest Pose & Load Models
	for bone_name, parent_name in pairs(topology) do
		local node = self.bones[bone_name]
		local bp = rest_pose[bone_name] -- [x, y, z]

		-- USER: THIS SPECIFIC OPERATION MAKES THE ANIMATION AND BONES LOOK CORRECT, BUT THE MESHES DISAPEAR
		if parent_name and self.bones[parent_name] then
			self.bones[parent_name]:attach(node)
			local pp = rest_pose[parent_name]
			-- Local position = Child World - Parent World
			node:set_position(vec3(bp[1] - pp[1], bp[2] - pp[2], bp[3] - pp[3]))
		else
			-- Root bone (e.g. Hips or 'root')
			self.char_root:attach(node)
			node:set_position(vec3(unpack(bp)))
		end
		-- END
		-- USER: UNCOMMENTING THIS AND COMMENTING THE OTHER ONE SHOWS MESHES BUT BONES ARE MESSED UP
		-- self.char_root:attach(node)
		-- node:set_position(vec3(unpack(bp)))
		-- END

		self:load_bone_model(bone_name)
	end

	-- Force update transforms to ensure positions are correct
	self.root:recursive_update_transform()
end

function App:update(dt)
	self.time = self.time + dt
	self:apply_animation(dt)

	-- Camera Controls
	if love.keyboard.isDown("left") then
		self.cam_angle = self.cam_angle - dt * 2
	end
	if love.keyboard.isDown("right") then
		self.cam_angle = self.cam_angle + dt * 2
	end
	if love.keyboard.isDown("up") then
		self.cam_dist = math.max(2, self.cam_dist - dt * 10)
	end
	if love.keyboard.isDown("down") then
		self.cam_dist = self.cam_dist + dt * 10
	end
	if love.keyboard.isDown("w") then
		self.cam_height = self.cam_height + dt * 5
	end
	if love.keyboard.isDown("s") then
		self.cam_height = self.cam_height - dt * 5
	end

	-- Skin Tint Controls
	local tint_speed = dt * 0.5
	if love.keyboard.isDown("r") then
		self.skin_tint[1] = self.skin_tint[1] + (love.keyboard.isDown("lshift") and tint_speed or -tint_speed)
	end
	if love.keyboard.isDown("g") then
		self.skin_tint[2] = self.skin_tint[2] + (love.keyboard.isDown("lshift") and tint_speed or -tint_speed)
	end
	if love.keyboard.isDown("b") then
		self.skin_tint[3] = self.skin_tint[3] + (love.keyboard.isDown("lshift") and tint_speed or -tint_speed)
	end

	-- Clamp tint
	for i = 1, 3 do
		self.skin_tint[i] = math.max(0, math.min(1, self.skin_tint[i]))
	end

	if love.keyboard.isDown("1") and not self.k_1_down then
		self.show_skeleton = not self.show_skeleton
		self.k_1_down = true
	elseif not love.keyboard.isDown("1") then
		self.k_1_down = false
	end

	if love.keyboard.isDown("2") and not self.k_2_down then
		self.show_mesh = not self.show_mesh
		self.k_2_down = true
	elseif not love.keyboard.isDown("2") then
		self.k_2_down = false
	end

	-- Update Cameras
	local aspect = self.view_w / self.view_h
	local o_size = 30 -- Ortho size covers whole body

	-- View 1: Front (Ortho)
	self.views[1].camera.m_projection:ortho_RH_NO(-o_size * aspect, o_size * aspect, -o_size, o_size, -200, 200)
	self.views[1].camera.eye = vec3(0, 25, 100)
	self.views[1].camera.center = vec3(0, 25, 0)
	self.views[1].camera:update_view_matrix()

	-- View 2: Side (Ortho)
	self.views[2].camera.m_projection:ortho_RH_NO(-o_size * aspect, o_size * aspect, -o_size, o_size, -200, 200)
	self.views[2].camera.eye = vec3(100, 25, 0)
	self.views[2].camera.center = vec3(0, 25, 0)
	self.views[2].camera:update_view_matrix()

	-- View 3 & 4: Perspective Orbit
	for i = 3, 4 do
		local cam = self.views[i].camera
		cam.m_projection:perspective_RH_NO(40, aspect, 0.1, 1000)
		cam.eye.x = math.cos(self.cam_angle) * self.cam_dist
		cam.eye.z = math.sin(self.cam_angle) * self.cam_dist
		cam.eye.y = self.cam_height
		cam.center = self.cam_center
		cam:update_view_matrix()
	end
end

function App:render_view(idx, camera)
	local v = self.views[idx]
	love.graphics.setCanvas({ v.canvas, depthstencil = v.depth })
	love.graphics.clear(0.1, 0.1, 0.12, 1, true, true)
	love.graphics.setDepthMode("always", false) -- Disable depth test for debug
	love.graphics.setMeshCullMode("none")
	love.graphics.setColor(1, 1, 1, 1)

	self.env.camera = camera

	-- Update transforms
	self.root:recursive_update_transform()
	self.scene:update_nodes(self.root, self.env)

	-- Update Shader Uniforms
	if self.shader:hasUniform("eyePosition") then
		self.shader:send("eyePosition", { camera.eye:unpack() })
	end
	if self.shader:hasUniform("skinTint") then
		self.shader:send("skinTint", self.skin_tint)
	end
	if self.shader:hasUniform("skinTintStrength") then
		self.shader:send("skinTintStrength", self.skin_tint_strength)
	end

	-- Update Mesh Visibility
	-- if self.char_root then
	-- 	self.char_root:traverse(function(n)
	-- 		if n.is_model_node then
	-- 			n.render_flag = self.show_mesh
	-- 		end
	-- 	end)
	-- end

	-- Render
	self.scene:render_nodes(self.root, self.env)

	-- Draw Skeleton Lines (View 1 & 2 only)
	if idx <= 2 and self.bones and self.show_skeleton then
		love.graphics.setShader()
		love.graphics.setDepthMode("always", false) -- Draw on top?
		love.graphics.setColor(1, 1, 0, 1)

		for _, bone in pairs(self.bones) do
			local p1 = bone:get_world_position()
			local s1 = camera:world_to_screen_point(p1, { 0, 0, self.view_w, self.view_h })

			if s1.x > -100 and s1.x < self.view_w + 100 then
				love.graphics.circle("fill", s1.x, s1.y, 3)

				if bone.parent and self.bones[bone.parent.name] then
					local p2 = bone.parent:get_world_position()
					local s2 = camera:world_to_screen_point(p2, { 0, 0, self.view_w, self.view_h })
					love.graphics.line(s1.x, s1.y, s2.x, s2.y)
				end
			end
		end
	end

	love.graphics.setCanvas()
end

function App:draw()
	for i = 1, 4 do
		self:render_view(i, self.views[i].camera)
	end

	love.graphics.setShader()
	love.graphics.setColor(1, 1, 1)
	love.graphics.draw(self.views[1].canvas, 0, 0)
	love.graphics.draw(self.views[2].canvas, self.view_w, 0)
	love.graphics.draw(self.views[3].canvas, 0, self.view_h)
	love.graphics.draw(self.views[4].canvas, self.view_w, self.view_h)

	-- Dividers
	love.graphics.setColor(0, 0, 0)
	love.graphics.setLineWidth(2)
	love.graphics.line(self.view_w, 0, self.view_w, self.view_h * 2)
	love.graphics.line(0, self.view_h, self.view_w * 2, self.view_h)
	love.graphics.setLineWidth(1)

	-- Text
	love.graphics.setColor(1, 1, 1)
	love.graphics.print("1: Front (Ortho) - Skeleton", 10, 10)
	love.graphics.print("2: Side (Ortho) - Skeleton", self.view_w + 10, 10)
	love.graphics.print("3: Perspective", 10, self.view_h + 10)
	love.graphics.print("4: Perspective (Aux)", self.view_w + 10, self.view_h + 10)

	love.graphics.print(
		string.format("Skin Tint: %.2f, %.2f, %.2f", self.skin_tint[1], self.skin_tint[2], self.skin_tint[3]),
		10,
		self.view_h * 2 - 20
	)
end

function love.load()
	App:load()
end
function love.update(dt)
	App:update(dt)
end
function love.draw()
	App:draw()
end
