io.stdout:setvbuf("no")
local menori = require("menori")
local json = require("json")
local ml = menori.ml
local vec3 = ml.vec3
local quat = ml.quat

local Actor = require("actor")

local HEAD_PATH = "assets/hero/base_head.gltf"
local RIG_PATH = "assets/hero/rig.json"

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
	self.ref_sprite_img = love.graphics.newImage("assets/t_pose_sprite.png")

	-- 2. Scene Setup
	self.scene = menori.Scene()
	self.root = menori.Node("scene_root")
	self.env = menori.Environment(nil)

	-- Lighting
	self.env:set("ambientColor", { 0.2, 0.2, 0.25 })
	self.env:set("ambientIntensity", 1.0)
	self.env:set("dirLightDirection", { -0.6, -0.8, 0.5 })
	self.env:set("dirLightColor", { 1.5, 1.5, 1.4 })

	-- 3. Initialize Actor
	self.actor = Actor.new(RIG_PATH, "assets/hero", self.shader, self.palette)
	self.actor:load_animations("assets/hero")
	self.root:attach(self.actor.root)

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

	self.bone_colors = {
		mixamorig_Hips = { 1, 0, 0, 1 },
		mixamorig_Spine = { 0, 1, 0, 1 },
		mixamorig_Spine1 = { 0, 0, 1, 1 },
		mixamorig_Spine2 = { 1, 1, 0, 1 },
		mixamorig_Neck = { 1, 0, 1, 1 },
		mixamorig_Head = { 0, 1, 1, 1 },
		mixamorig_LeftShoulder = { 0.5, 0, 0, 1 },
		mixamorig_LeftArm = { 0, 0.5, 0, 1 },
		mixamorig_LeftForeArm = { 0, 0, 0.5, 1 },
		mixamorig_LeftHand = { 0.5, 0.5, 0, 1 },
		mixamorig_RightShoulder = { 0.5, 0, 0.5, 1 },
		mixamorig_RightArm = { 0, 0.5, 0.5, 1 },
		mixamorig_RightForeArm = { 0.8, 0.2, 0.2, 1 },
		mixamorig_RightHand = { 0.2, 0.8, 0.2, 1 },
		mixamorig_LeftUpLeg = { 0.2, 0.2, 0.8, 1 },
		mixamorig_LeftLeg = { 0.8, 0.8, 0.2, 1 },
		mixamorig_LeftFoot = { 0.8, 0.2, 0.8, 1 },
		mixamorig_RightUpLeg = { 0.2, 0.8, 0.8, 1 },
		mixamorig_RightLeg = { 0.5, 0.5, 0.5, 1 },
		mixamorig_RightFoot = { 1, 0.5, 0, 1 },
	}
end

function App:update(dt)
	self.time = self.time + dt
	self.actor:update(dt, self.animation_speed)

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

	if love.keyboard.isDown("tab") and not self.k_tab_down then
		self.actor:next_animation()
		self.k_tab_down = true
	elseif not love.keyboard.isDown("tab") then
		self.k_tab_down = false
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
	love.graphics.setDepthMode("lequal", true)
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

	-- Apply Colors before rendering
	local current_bone_colors = (idx == 4) and self.bone_colors or nil
	self.actor:set_model_colors({1, 1, 1, 1}, current_bone_colors)

	-- Render Reference Sprite (View 1 only)
	if idx == 1 and self.ref_sprite_img then
		love.graphics.setShader()
		love.graphics.setDepthMode("always", false)

		local iw, ih = self.ref_sprite_img:getDimensions()
		local world_h = 50 -- Match rig height
		local o_size = 30
		local scale = (world_h * (self.view_h / (o_size * 2))) / ih

		-- Screen center corresponds to world (0, 25, 0)
		-- Sprite base should be at world y=0
		-- In ortho view, world y=0 is (25 units below center)
		-- 25 units in pixels = 25 * (view_h / 60)
		local screen_y_base = (self.view_h / 2) + (25 * (self.view_h / 60))

		love.graphics.setColor(1, 1, 1, 0.4) -- Faded
		love.graphics.draw(
			self.ref_sprite_img,
			self.view_w / 2,
			screen_y_base,
			0,
			scale,
			scale,
			iw / 2,
			ih
		)
		love.graphics.setColor(1, 1, 1, 1)
		love.graphics.setDepthMode("lequal", true)
	end

	-- Render using standard engine path
	self.actor.mesh_root.visible = self.show_mesh
	self.scene:render_nodes(self.root, self.env)

	-- Draw Skeleton Lines (View 1 & 2 only)
	if idx <= 2 and self.show_skeleton then
		self.actor:draw_skeleton(camera, { 0, 0, self.view_w, self.view_h })
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
	love.graphics.print("4: Bone Visualization", self.view_w + 10, self.view_h + 10)

	-- Legend for View 4
	if self.bone_colors then
		local ly = self.view_h + 30
		local lx = self.view_w + 10
		local i = 0
		-- Sort keys for stable legend
		local keys = {}
		for k in pairs(self.bone_colors) do
			table.insert(keys, k)
		end
		table.sort(keys)

		for _, name in ipairs(keys) do
			local color = self.bone_colors[name]
			love.graphics.setColor(color)
			love.graphics.rectangle("fill", lx, ly, 10, 10)
			love.graphics.setColor(1, 1, 1)
			love.graphics.print(name:gsub("mixamorig_", ""), lx + 15, ly - 2)
			ly = ly + 14
			i = i + 1
			if i % 15 == 0 then
				lx = lx + 100
				ly = self.view_h + 30
			end
		end
	end

	love.graphics.setColor(1, 1, 1)
	local anim_name = self.actor:get_active_animation_name()
	love.graphics.print("Animation: " .. anim_name .. " (Tab to switch)", 10, self.view_h * 2 - 40)

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
