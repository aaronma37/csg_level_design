local menori = require("menori")
local json = require("json")
local ml = menori.ml
local vec3 = ml.vec3
local quat = ml.quat

local RIG_PATH = "hero_rigged.json"
local ANIM_PATH = "hero_anim.json"

local App = {
	time = 0,
	animation_speed = 12,

	-- Camera Params
	cam_angle = math.pi / 4, -- 45 degrees for isometric feel
	cam_dist = 150,
	cam_height = 80,         -- Elevated for isometric look
	cam_center = vec3(0, 25, 0),

	-- Skin Tint
	skin_tint = { 1.0, 0.7, 0.7 }, -- Default to slight red tint
	skin_tint_strength = 1.0,      -- Default to full strength
}

local DEBUG_COLORS = {
	{ 1, 0, 0 },
	{ 0, 1, 0 },
	{ 0, 0, 1 },
	{ 1, 1, 0 },
	{ 1, 0, 1 },
	{ 0, 1, 1 },
	{ 1, 0.5, 0 },
	{ 0.5, 1, 0 },
	{ 0, 0.5, 1 },
}

function App:load()
	love.graphics.setDefaultFilter("nearest", "nearest")

	-- 1. Load Custom Shader (Restored)
	-- Wrap in pcall to catch compilation errors
	local status, shader_or_err = pcall(love.graphics.newShader, "shaders/lighting.glsl")
	if status then
		self.shader = shader_or_err
		self.shader_error = nil
	else
		self.shader_error = shader_or_err
		print("Shader Error:", self.shader_error)
		-- Fallback to a dummy shader to prevent crash, though it won't light up
		self.shader = love.graphics.newShader([[
			vec4 effect(vec4 color, Image tex, vec2 texture_coords, vec2 screen_coords) {
				return Texel(tex, texture_coords) * color;
			}
		]])
	end
	
	self.palette = love.graphics.newImage("assets/palette_texture.png")

	local ok, res = pcall(love.graphics.newImage, "assets/t_pose_sprite.png")
	if ok then
		self.tpose_sprite_tex = res
	end

	-- 2. Load Data
	local f = io.open(RIG_PATH, "r")
	if f then
		self.rig_data = json.decode(f:read("*all"))
		f:close()
	end
	local f_anim = io.open(ANIM_PATH, "r")
	if f_anim then
		self.anim_data = json.decode(f_anim:read("*all"))
		f_anim:close()
	end

	-- 3. Scene
	self.scene = menori.Scene()
	self.root = menori.Node("scene_root")
	self.env = menori.Environment(nil)

	-- Lighting Settings (High contrast for voxel edges)
	self.env:set("ambientColor", { 0.2, 0.2, 0.25 })
	self.env:set("ambientIntensity", 1.0)
	self.env:set("dirLightDirection", { -0.6, -0.8, 0.5 })
	self.env:set("dirLightColor", { 1.5, 1.5, 1.4 })

	-- Floor
	local floor_mesh = menori.Plane(200, 200)
	local floor_mat = menori.Material()
	floor_mat:set("baseColor", { 0.3, 0.3, 0.3, 1 })
	floor_mat:set_shader(self.shader)
	self.floor_node = menori.ModelNode(floor_mesh, floor_mat)
	self.floor_node:set_rotation(quat.from_angle_axis(-math.pi / 2, vec3.unit_x))
	self.root:attach(self.floor_node)

	-- Character
	if self.rig_data then
		self.char_root = menori.Node("char_root")
		self.char_root:set_position(vec3(0, 1, 0))
		self.root:attach(self.char_root)
		self:build_skeleton(self.char_root)
	end

	-- Reference Quad
	if self.tpose_sprite_tex then
		local w, h = 54, 64
		local ref_mesh = menori.Plane(w, h)
		local ref_mat = menori.Material()
		ref_mat.main_texture = self.tpose_sprite_tex
		ref_mat:set_shader(self.shader)
		ref_mat.alpha_mode = "BLEND"
		ref_mat:set("baseColor", { 1, 1, 1, 0.4 })
		ref_mat:set("unlit", true)
		self.ref_sprite_node = menori.ModelNode(ref_mesh, ref_mat)
		self.ref_sprite_node:set_position(vec3(0, 27, -10))
		self.root:attach(self.ref_sprite_node)
	end

	-- 4. View Setup
	local win_w, win_h = love.graphics.getDimensions()
	self.view_w, self.view_h = math.floor(win_w / 2), math.floor(win_h / 2)

	self.views = {}
	for i = 1, 4 do
		self.views[i] = {
			canvas = love.graphics.newCanvas(self.view_w, self.view_h),
			depth = love.graphics.newCanvas(self.view_w, self.view_h, { format = "depth24" }),
			camera = menori.Camera3D((i <= 2) and "ortho" or "perspective", { fov = 40, ortho_size = 60 }),
		}
	end

	local white = love.image.newImageData(1, 1)
	white:setPixel(0, 0, 1, 1, 1, 1)
	self.white_tex = love.graphics.newImage(white)
end

function App:build_voxel_mesh(voxels)
	local vertices = {}
	-- Match our restored shader and standard Menori format
	local format = {
		{ "VertexPosition", "float", 3 },
		{ "VertexNormal", "float", 3 },
		{ "VertexColor", "float", 4 },
		{ "VertexTexCoord", "float", 2 },
	}
	for _, v in ipairs(voxels) do
		local vx, vy, vz, c = v[1], v[2], v[3], v[4]
		local u = (c + 0.5) / 256.0
		local x, y, z = vx, vy, vz
		local faces = {
			{ n = { 0, 1, 0 }, v = { { 0, 1, 1 }, { 1, 1, 1 }, { 1, 1, 0 }, { 0, 1, 0 } } }, -- Top (Reordered to CCW)
			{ n = { 0, -1, 0 }, v = { { 0, 0, 0 }, { 1, 0, 0 }, { 1, 0, 1 }, { 0, 0, 1 } } }, -- Bottom (Reordered to CCW)
			{ n = { 0, 0, 1 }, v = { { 0, 0, 1 }, { 1, 0, 1 }, { 1, 1, 1 }, { 0, 1, 1 } } }, -- Front
			{ n = { 0, 0, -1 }, v = { { 1, 0, 0 }, { 0, 0, 0 }, { 0, 1, 0 }, { 1, 1, 0 } } }, -- Back
			{ n = { 1, 0, 0 }, v = { { 1, 0, 0 }, { 1, 0, 1 }, { 1, 1, 1 }, { 1, 1, 0 } } }, -- Right
			{ n = { -1, 0, 0 }, v = { { 0, 0, 1 }, { 0, 0, 0 }, { 0, 1, 0 }, { 0, 1, 1 } } }, -- Left
		}
		for _, f in ipairs(faces) do
			for _, i in ipairs({ 1, 3, 2, 1, 4, 3 }) do -- Reverse to CW
				local vert = f.v[i]
				table.insert(vertices, {
					x + vert[1],
					y + vert[2],
					z + vert[3],
					f.n[1],
					f.n[2],
					f.n[3],
					1,
					1,
					1,
					1,
					u,
					0.5,
				})
			end
		end
	end
	return menori.Mesh({ vertices = vertices, vertexformat = format })
end

function App:build_skeleton(parent_node)
	self.bones = {}
	self.standard_mesh_nodes = {}
	self.debug_mesh_nodes = {}
	local rest_pose = self.rig_data.skeleton.rest_pose
	local topology = self.rig_data.skeleton.topology
	local parts = self.rig_data.parts

	for bone_name, _ in pairs(rest_pose) do
		self.bones[bone_name] = menori.Node(bone_name)
	end
	for bone_name, parent_name in pairs(topology) do
		local node = self.bones[bone_name]
		local bp = rest_pose[bone_name]
		if parent_name and self.bones[parent_name] then
			self.bones[parent_name]:attach(node)
			node:set_position(vec3(unpack(bp)) - vec3(unpack(rest_pose[parent_name])))
		else
			parent_node:attach(node)
			node:set_position(vec3(unpack(bp)))
		end
	end

	-- Deterministic sorting for bone colors
	local sorted_bone_names = {}
	for name, _ in pairs(self.bones) do table.insert(sorted_bone_names, name) end
	table.sort(sorted_bone_names)

	local color_idx = 1
	for _, bone_name in ipairs(sorted_bone_names) do
		local node = self.bones[bone_name]
		if not node.parent then
			parent_node:attach(node)
		end

		if parts[bone_name] and #parts[bone_name].voxels > 0 then
			local mesh = self:build_voxel_mesh(parts[bone_name].voxels)
			-- Standard
			local mat = menori.Material()
			mat.main_texture = self.palette
			mat:set_shader(self.shader)
			mat:set("unlit", false)
			local mnode = menori.ModelNode(mesh, mat)
			mnode.material:set_shader(self.shader) -- FORCE shader after ModelNode init
			node:attach(mnode)
			table.insert(self.standard_mesh_nodes, mnode)
			-- Debug
			local dmat = menori.Material()
			dmat.main_texture = self.white_tex
			local c = DEBUG_COLORS[((color_idx - 1) % #DEBUG_COLORS) + 1]
			dmat:set("baseColor", { c[1], c[2], c[3], 1 })
			dmat:set_shader(self.shader)
			dmat:set("unlit", false)
			local dnode = menori.ModelNode(mesh, dmat)
			dnode.material:set_shader(self.shader) -- FORCE shader here too
			node:attach(dnode)
			table.insert(self.debug_mesh_nodes, dnode)
			color_idx = color_idx + 1
		end
	end
end

function App:update(dt)
	self.time = self.time + dt
	if love.keyboard.isDown("left") then
		self.cam_angle = self.cam_angle - dt * 2
	end
	if love.keyboard.isDown("right") then
		self.cam_angle = self.cam_angle + dt * 2
	end
	if love.keyboard.isDown("up") then
		self.cam_dist = math.max(10, self.cam_dist - dt * 100)
	end
	if love.keyboard.isDown("down") then
		self.cam_dist = self.cam_dist + dt * 100
	end
	if love.keyboard.isDown("w") then
		self.cam_height = self.cam_height + dt * 100
	end
	if love.keyboard.isDown("s") then
		self.cam_height = self.cam_height - dt * 100
	end

	-- Skin Tint Controls
	local tint_speed = dt * 0.5
	if love.keyboard.isDown("r") then
		if love.keyboard.isDown("lshift") then
			self.skin_tint[1] = math.min(1, self.skin_tint[1] + tint_speed)
		else
			self.skin_tint[1] = math.max(0, self.skin_tint[1] - tint_speed)
		end
	end
	if love.keyboard.isDown("g") then
		if love.keyboard.isDown("lshift") then
			self.skin_tint[2] = math.min(1, self.skin_tint[2] + tint_speed)
		else
			self.skin_tint[2] = math.max(0, self.skin_tint[2] - tint_speed)
		end
	end
	if love.keyboard.isDown("b") then
		if love.keyboard.isDown("lshift") then
			self.skin_tint[3] = math.min(1, self.skin_tint[3] + tint_speed)
		else
			self.skin_tint[3] = math.max(0, self.skin_tint[3] - tint_speed)
		end
	end
	if love.keyboard.isDown("t") then
		if love.keyboard.isDown("lshift") then
			self.skin_tint_strength = math.min(1, self.skin_tint_strength + tint_speed)
		else
			self.skin_tint_strength = math.max(0, self.skin_tint_strength - tint_speed)
		end
	end

	local aspect = self.view_w / self.view_h
	local o_size = 60
	for i = 1, 2 do
		local cam = self.views[i].camera
		cam.m_projection:ortho_RH_NO(-o_size * aspect, o_size * aspect, -o_size, o_size, -200, 200)
		cam.eye = vec3(0, 25, 100)
		cam.center = vec3(0, 25, 0)
		cam:update_view_matrix()
	end
	for i = 3, 4 do
		local cam = self.views[i].camera
		cam.m_projection:perspective_RH_NO(40, aspect, 0.1, 1000)
		cam.eye.x, cam.eye.z, cam.eye.y =
			math.cos(self.cam_angle) * self.cam_dist, math.sin(self.cam_angle) * self.cam_dist, self.cam_height
		cam.center = vec3(0, 25, 0)
		cam:update_view_matrix()
	end
end

function App:render_view(idx, camera, is_tpose, show_mesh, asset_debug)
	local v = self.views[idx]
	love.graphics.setCanvas({ v.canvas, depthstencil = v.depth })
	love.graphics.clear(0.1, 0.1, 0.12, 1, true, true)
	love.graphics.setDepthMode("lequal", true)
	love.graphics.setColor(1, 1, 1, 1)

	if is_tpose then
		for _, n in pairs(self.bones) do
			n:set_rotation(quat())
		end
	elseif self.anim_data then
		local frame = self.anim_data.frames[math.floor(self.time * self.animation_speed) % self.anim_data.duration + 1]
		for b, data in pairs(frame) do
			if self.bones[b] then
				-- Handle rotation
				if data.rot then
					self.bones[b]:set_rotation(quat.from_euler_angles(unpack(data.rot)))
				end
				-- Handle translation (Pelvis bob)
				if b == "pelvis" and data.pos then
					local rest_pos = self.rig_data.skeleton.rest_pose[b]
					-- We only want the RELATIVE movement (bobbing)
					-- Mixamo root is usually at (0,0,0) in the DAE, 
					-- so we add its movement to our rest position.
					-- We zero out the Z (forward) movement to keep it in place for the preview.
					local dx, dy, dz = data.pos[1], data.pos[2], data.pos[3]
					self.bones[b]:set_position(vec3(rest_pos[1] + dx, rest_pos[2] + dy, rest_pos[3]))
				end
			end
		end
	end

	for _, m in ipairs(self.standard_mesh_nodes) do
		m.render_flag = (show_mesh and not asset_debug)
		m.material:set("baseColor", { 1, 1, 1, (idx == 2 and 0.5 or 1) })
		m.material.alpha_mode = (idx == 2 and "BLEND" or "OPAQUE")
	end
	for _, m in ipairs(self.debug_mesh_nodes) do
		m.render_flag = (show_mesh and asset_debug)
	end
	self.floor_node.render_flag = (idx >= 3)
	if self.ref_sprite_node then
		self.ref_sprite_node.render_flag = (idx <= 2)
	end

	self.env.camera = camera
	self.root:traverse(function(n)
		n._transform_flag = true
	end)
	self.scene:update_nodes(self.root, self.env)

	-- Manual Shader Update
	if self.shader:hasUniform("m_view") then
		self.shader:send("m_view", "column", camera.m_view.data)
	end
	local proj = camera.m_projection:clone()
	proj[6] = -proj[6]
	if self.shader:hasUniform("m_projection") then
		self.shader:send("m_projection", "column", proj.data)
	end
	if self.shader:hasUniform("eyePosition") then
		self.shader:send("eyePosition", { camera.eye:unpack() })
	end
	if self.shader:hasUniform("skinTint") then
		self.shader:send("skinTint", self.skin_tint)
	end
	if self.shader:hasUniform("skinTintStrength") then
		self.shader:send("skinTintStrength", self.skin_tint_strength)
	end

	self.scene:render_nodes(self.root, self.env)

	if idx == 1 or idx == 2 then
		love.graphics.setColor(1, 1, 0)
		for _, node in pairs(self.bones) do
			local sp = camera:world_to_screen_point(node:get_world_position(), { 0, 0, self.view_w, self.view_h })
			if sp.x > 0 then
				love.graphics.circle("fill", sp.x, sp.y, 4)
				if node.parent and self.bones[node.parent.name] then
					local sp2 = camera:world_to_screen_point(
						node.parent:get_world_position(),
						{ 0, 0, self.view_w, self.view_h }
					)
					love.graphics.line(sp.x, sp.y, sp2.x, sp2.y)
				end
			end
		end
	end
	love.graphics.setCanvas()
end

function App:draw()
	self:render_view(1, self.views[1].camera, true, false, false)
	self:render_view(2, self.views[2].camera, true, true, false)
	self:render_view(3, self.views[3].camera, false, true, false)
	self:render_view(4, self.views[4].camera, false, true, true)

	love.graphics.setShader()
	love.graphics.setColor(1, 1, 1)
	love.graphics.draw(self.views[1].canvas, 0, 0)
	love.graphics.draw(self.views[2].canvas, self.view_w, 0)
	love.graphics.draw(self.views[3].canvas, 0, self.view_h)
	love.graphics.draw(self.views[4].canvas, self.view_w, self.view_h)

	love.graphics.line(self.view_w, 0, self.view_w, self.view_h * 2)
	love.graphics.line(0, self.view_h, self.view_w * 2, self.view_h)
	love.graphics.print("1: Skeleton Reference", 10, 10)
	love.graphics.print("2: Mesh Alignment", self.view_w + 10, 10)
	love.graphics.print("3: Animation Preview", 10, self.view_h + 10)
	love.graphics.print("4: Bone Asset Debug", self.view_w + 10, self.view_h + 10)
	
	-- Legend for View 4
	local lx, ly = self.view_w + 10, self.view_h + 30
	local color_idx = 1
	-- Sort bones so legend is consistent
	local sorted_bones = {}
	for name, _ in pairs(self.bones) do table.insert(sorted_bones, name) end
	table.sort(sorted_bones)

	for _, name in ipairs(sorted_bones) do
		local parts = self.rig_data.parts
		if parts[name] and #parts[name].voxels > 0 then
			local c = DEBUG_COLORS[((color_idx - 1) % #DEBUG_COLORS) + 1]
			love.graphics.setColor(c[1], c[2], c[3])
			love.graphics.rectangle("fill", lx, ly, 10, 10)
			love.graphics.setColor(1, 1, 1)
			love.graphics.print(name, lx + 15, ly - 2)
			ly = ly + 15
			color_idx = color_idx + 1
		end
	end

	love.graphics.print(
		string.format(
			"Skin Tint (R/G/B/T): %.2f, %.2f, %.2f | %.2f",
			self.skin_tint[1],
			self.skin_tint[2],
			self.skin_tint[3],
			self.skin_tint_strength
		),
		10,
		self.view_h * 2 - 20
	)

	if self.shader_error then
		love.graphics.setColor(1, 0, 0)
		love.graphics.print("SHADER ERROR: " .. tostring(self.shader_error), 10, self.view_h * 2 - 40)
		love.graphics.setColor(1, 1, 1)
	end
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
