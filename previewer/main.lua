-- CSG Level Previewer (Aligned with love_exp)
local menori = require("menori")
local ml = menori.ml
local vec3 = ml.vec3
local quat = ml.quat

local layout_name = "tavern_layout"
local screenshot_path = nil
local use_ortho = true
local model_path = nil
local is_unlit = false

-- Simple arg parsing
for i, v in ipairs(arg) do
	if v == "--screenshot" and arg[i + 1] then
		screenshot_path = arg[i + 1]
	elseif v == "--perspective" then
		use_ortho = false
	elseif v == "--unlit" then
		is_unlit = true
	elseif v == "--model" and arg[i + 1] then
		model_path = arg[i + 1]
	elseif v ~= "previewer/" and not v:find("^--") then
		layout_name = v
	end
end

local Scene = {}

function love.load()
	love.graphics.setDefaultFilter("nearest", "nearest")

	-- Load Shaders
	Scene.lightingShader = love.graphics.newShader("shaders/lighting.glsl")
	Scene.shadowShader = love.graphics.newShader("shaders/shadow.glsl")
	Scene.gradientShader = love.graphics.newShader("shaders/gradient.glsl")

	-- Load Assets
	Scene.paletteTexture = love.graphics.newImage("assets/palette_texture.png")

	-- Setup Scene
	Scene.scene = menori.Scene()
	Scene.root_node = menori.Node()
	Scene.camera = menori.Camera3D(use_ortho and "ortho" or "perspective", { fov = 20, ortho_size = 15 })
	Scene.environment = menori.Environment(Scene.camera)

	-- Setup Camera
	Scene.camera.eye = vec3(0, 30, 30)
	Scene.camera.center = vec3(15, 5, 15)
	Scene.camera.up = vec3(0, 1, 0)
	Scene.camera:update_projection()
	Scene.camera:update_view_matrix()

	-- Dummy Textures for required uniforms
	local whiteData = love.image.newImageData(1, 1)
	whiteData:setPixel(0, 0, 1, 1, 1, 1)
	Scene.whiteTexture = love.graphics.newImage(whiteData)

	-- Set environment uniforms (automatic transmission)
	Scene.environment:set("isProcedural", 1.0)
	Scene.environment:set("ssaoTex", Scene.whiteTexture)
	Scene.environment:set("showIndices", false)
	Scene.environment:set("numLights", 0)
	Scene.environment:set("fogColor", { 0.15, 0.15, 0.18 })
	Scene.environment:set("fogNear", 30.0)
	Scene.environment:set("fogFar", 100.0)

	-- Load Layout or Single Model
	Scene.bounds = { min_x = 1000, max_x = -1000, min_z = 1000, max_z = -1000 }

	if model_path then
		print("Loading single model: " .. model_path)
		local gltf_data = menori.glTFLoader.load(model_path)
		local scenes_nodes = menori.NodeTreeBuilder.create(gltf_data, function(scene, builder)
			scene:traverse(function(node)
				if node.is_model_node then
					-- node.material.main_texture = Scene.paletteTexture
					node.material:set_shader(Scene.lightingShader)
					node.material:set("isProcedural", 1.0)
					if node.material.alpha_mode ~= "OPAQUE" then
						node.material.alpha_mode = "MASK"
						node.material.alpha_cutoff = 0.5
					end
					node.material.mesh_cull_mode = "none"
				end
			end)
		end)

		if scenes_nodes[1] then
			for _, child in ipairs(scenes_nodes[1].children) do
				local s = 0.1
				-- Center at origin
				child:set_position(vec3(0, 0, 0))
				child:set_scale(vec3(s, s, s))

				Scene.root_node:attach(child)
			end
		end

		-- Focus camera on origin for single model
		Scene.camera.center = vec3(0, 3, 0)
		Scene.cameraDistance = 12
	else
		package.path = package.path .. ";assets/?.lua"
		local ok, layout = pcall(require, "csg_assets.scenes." .. layout_name)
		if not ok then
			print("Failed to load layout: " .. layout_name)
			print(layout)
			love.event.quit()
			return
		end

		for _, item in ipairs(layout) do
			local gltf_path = "assets/csg_assets/" .. item.asset_id .. ".gltf"
			local info = love.filesystem.getInfo(gltf_path)
			if info then
				local gltf_data = menori.glTFLoader.load(gltf_path)
				local scenes_nodes = menori.NodeTreeBuilder.create(gltf_data, function(scene, builder)
					scene:traverse(function(node)
						if node.is_model_node then
							-- node.material.main_texture = Scene.paletteTexture
							node.material:set_shader(Scene.lightingShader)
							node.material:set("isProcedural", 1.0)
							if node.material.alpha_mode ~= "OPAQUE" then
								node.material.alpha_mode = "MASK"
								node.material.alpha_cutoff = 0.5
							end
							node.material.mesh_cull_mode = "none"
						end
					end)
				end)

				if scenes_nodes[1] then
					-- Direct children attachment to avoid container node issues
					for _, child in ipairs(scenes_nodes[1].children) do
						local s = 0.1
						local x, y, z = item.pos[1] * s, item.pos[3] * s, item.pos[2] * s

						child:set_position(vec3(x, y, z))
						child:set_scale(vec3(s, s, s))
						child:set_rotation(quat.from_euler_angles(0, math.rad(item.rot), 0))

						Scene.root_node:attach(child)

						Scene.bounds.min_x = math.min(Scene.bounds.min_x, x)
						Scene.bounds.max_x = math.max(Scene.bounds.max_x, x)
						Scene.bounds.min_z = math.min(Scene.bounds.min_z, z)
						Scene.bounds.max_z = math.max(Scene.bounds.max_z, z)
					end
				end
			end
		end
	end

	Scene.bounds = { min_x = 1000, max_x = -1000, min_z = 1000, max_z = -1000 }
	-- DEEP DIRTY FLAG (Ensures Scene:render_nodes updates everything)
	Scene.root_node:traverse(function(n)
		n._transform_flag = true
	end)
	Scene.root_node:recursive_update_transform(true)

	-- Floor (Grid hack)
	local floor_mesh = menori.Plane(100, 100)
	local floor_material = menori.Material()
	local gridData = love.image.newImageData(128, 128)
	for gy = 0, 127 do
		for gx = 0, 127 do
			local c = (gx == 0 or gy == 0) and 1 or 0.2
			gridData:setPixel(gx, gy, c, c, c, 1)
		end
	end
	Scene.gridTexture = love.graphics.newImage(gridData)
	Scene.gridTexture:setWrap("repeat", "repeat")

	floor_material.main_texture = Scene.gridTexture
	floor_material:set_shader(Scene.lightingShader)
	floor_material:set("isProcedural", 0.0)
	Scene.floor = menori.ModelNode(floor_mesh, floor_material)
	Scene.floor:set_position(vec3(16, -0.5, 15))
	Scene.floor:set_rotation(quat.from_angle_axis(-math.pi / 2, vec3.unit_x))
	Scene.root_node:attach(Scene.floor)

	-- Lighting Defaults (Match game)
	Scene.ambientColor = { 0.300, 0.300, 0.350 }
	Scene.ambientIntensity = 2.565
	Scene.dirLightDirection = { -0.600, -0.461, 0.348 }
	Scene.dirLightColor = { 0.800, 0.800, 0.700 }

	-- Shadow Map Setup
	Scene.shadowCanvas = love.graphics.newCanvas(2048, 2048, { format = "rgba32f" })
	Scene.shadowDepthBuffer = love.graphics.newCanvas(2048, 2048, { format = "depth24" })

	-- Interaction State
	Scene.cameraAngle = 210 * math.pi / 180
	Scene.cameraDistance = 50
	Scene.cameraHeight = 15
end
function love.update(dt)
	-- Speed multipliers
	local moveSpeed = 40 * dt
	local rotSpeed = 2 * dt
	local zoomSpeed = 50 * dt

	-- Panning (WASD) - Moves the center point
	if love.keyboard.isDown("w") then
		Scene.camera.center.z = Scene.camera.center.z - moveSpeed
	end
	if love.keyboard.isDown("s") then
		Scene.camera.center.z = Scene.camera.center.z + moveSpeed
	end
	if love.keyboard.isDown("a") then
		Scene.camera.center.x = Scene.camera.center.x - moveSpeed
	end
	if love.keyboard.isDown("d") then
		Scene.camera.center.x = Scene.camera.center.x + moveSpeed
	end

	-- Vertical (QE)
	if love.keyboard.isDown("q") then
		Scene.camera.center.y = Scene.camera.center.y + moveSpeed
	end
	if love.keyboard.isDown("e") then
		Scene.camera.center.y = Scene.camera.center.y - moveSpeed
	end

	-- Orbit Rotation (Arrows)
	if love.keyboard.isDown("left") then
		Scene.cameraAngle = Scene.cameraAngle - rotSpeed
	end
	if love.keyboard.isDown("right") then
		Scene.cameraAngle = Scene.cameraAngle + rotSpeed
	end
	if love.keyboard.isDown("up") then
		Scene.cameraHeight = Scene.cameraHeight + moveSpeed
	end
	if love.keyboard.isDown("down") then
		Scene.cameraHeight = Scene.cameraHeight - moveSpeed
	end

	-- Mouse Rotation (Right Click)
	if love.mouse.isDown(2) then
		local mx, my = love.mouse.getPosition()
		if Scene.lastMouseX then
			local dx = mx - Scene.lastMouseX
			local dy = my - Scene.lastMouseY
			Scene.cameraAngle = Scene.cameraAngle + dx * 0.005
			Scene.cameraHeight = Scene.cameraHeight + dy * 0.1
		end
		Scene.lastMouseX, Scene.lastMouseY = mx, my
	else
		Scene.lastMouseX, Scene.lastMouseY = nil, nil
	end

	-- Zoom (Home/End or Mouse Wheel via callback)
	if love.keyboard.isDown("home") then
		Scene.cameraDistance = math.max(2, Scene.cameraDistance - zoomSpeed)
	end
	if love.keyboard.isDown("end") then
		Scene.cameraDistance = Scene.cameraDistance + zoomSpeed
	end

	-- Update Eye Position based on Orbit
	Scene.camera.eye.x = math.cos(Scene.cameraAngle) * Scene.cameraDistance + Scene.camera.center.x
	Scene.camera.eye.z = math.sin(Scene.cameraAngle) * Scene.cameraDistance + Scene.camera.center.z
	Scene.camera.eye.y = Scene.cameraHeight + Scene.camera.center.y

	Scene.camera:update_view_matrix()

	-- Update all node transforms down the hierarchy
	Scene.scene:update_nodes(Scene.root_node, Scene.environment)
end

function love.wheelmoved(x, y)
	if Scene.camera.mode == "ortho" then
		Scene.camera.params.ortho_size = math.max(1, (Scene.camera.params.ortho_size or 10) - y)
		Scene.camera:update_projection()
	else
		Scene.cameraDistance = math.max(2, Scene.cameraDistance - y * 5)
	end
end
function love.draw()
	local w, h = love.graphics.getDimensions()

	-- MUST update transforms before rendering
	Scene.scene:update_nodes(Scene.root_node, Scene.environment)

	-- 1. Shadow Pass
	local lightDir = vec3(unpack(Scene.dirLightDirection)):normalize()
	local lightPos = lightDir * -50.0
	local lightView = ml.mat4():look_at_RH(lightPos, vec3(0, 0, 0), vec3(0, 1, 0))
	local lightProj = ml.mat4():ortho_RH_NO(-40, 40, -40, 40, 0.1, 200)

	local shadowProj = lightProj:clone()
	shadowProj[6] = -shadowProj[6] -- Flip for canvas
	local lightSpaceMatrix = shadowProj * lightView

	love.graphics.setCanvas({ Scene.shadowCanvas, depthstencil = Scene.shadowDepthBuffer })
	love.graphics.clear({ 1, 1, 1, 1 }, true, true)
	love.graphics.setDepthMode("lequal", true)
	love.graphics.setShader(Scene.shadowShader)
	Scene.shadowShader:send("m_view", "column", lightView.data)
	Scene.shadowShader:send("m_projection", "column", shadowProj.data)

	Scene.root_node:traverse(function(node)
		if node.is_model_node then
			local original_shader = node.material.shader
			node.material.shader = Scene.shadowShader
			if Scene.shadowShader:hasUniform("m_model") then
				Scene.shadowShader:send("m_model", "column", node.world_matrix.data)
			end
			node.mesh:draw(node.material)
			node.material.shader = original_shader
		end
	end)
	love.graphics.setShader()
	love.graphics.setCanvas()

	-- 2. Main Pass
	if model_path then
		love.graphics.clear(0.8, 0.8, 0.8, 1, true, true)
	else
		love.graphics.clear(0.1, 0.1, 0.15, 1, true, true)
	end

	love.graphics.setDepthMode("lequal", true)

	-- Update environment uniforms (for automatic transmission)
	Scene.environment:set("shadowMap", Scene.shadowCanvas)
	Scene.environment:set("ssaoTex", Scene.whiteTexture)
	Scene.environment:set("isProcedural", 1.0)
	Scene.environment:set("showIndices", false) -- BACK TO REAL RENDERING
	Scene.environment:set("ambientColor", { 0.300, 0.300, 0.350 })
	Scene.environment:set("ambientIntensity", 2.565)
	Scene.environment:set("dirLightDirection", Scene.dirLightDirection)
	Scene.environment:set("dirLightColor", Scene.dirLightColor)
	Scene.environment:set("eyePosition", { Scene.camera.eye:unpack() })

	-- Manual matrix/array send for custom uniforms
	Scene.lightingShader:send("lightSpaceMatrix", "column", lightSpaceMatrix.data)
	Scene.lightingShader:send("numLights", 1)
	Scene.lightingShader:send("showIndices", false)
	local light_pos = { 16, 20, 15 } -- Light from above the tavern center
	Scene.lightingShader:send("lightPositions", light_pos)
	Scene.lightingShader:send("lightColors", { 1, 1, 1 })
	Scene.lightingShader:send("lightIntensities", 50.0)
	Scene.lightingShader:send("unlit", is_unlit)

	-- Render nodes
	Scene.scene:render_nodes(Scene.root_node, Scene.environment)

	if screenshot_path then
		love.graphics.captureScreenshot(function(imageData)
			local data = imageData:encode("png")
			local f = io.open(screenshot_path, "wb")
			if f then
				f:write(data:getString())
				f:close()
				print("Screenshot saved to: " .. screenshot_path)
			else
				print("Failed to save screenshot to: " .. screenshot_path)
			end
			love.event.quit()
		end)
	end

	-- UI / Debug Text
	if not screenshot_path then
		love.graphics.setShader()
		love.graphics.setColor(1, 1, 1, 1)
		love.graphics.print("Layout: " .. layout_name, 20, 20)
		love.graphics.print("WASD: Pan | QE: Up/Down | Drag Right Click: Rotate | Scroll: Zoom", 20, 40)
	end
end

function love.keypressed(key)
	if key == "escape" then
		love.event.quit()
	elseif key == "c" then
		local new_mode = Scene.camera.mode == "perspective" and "ortho" or "perspective"
		Scene.camera:set_mode(new_mode)
		print("Camera mode: " .. new_mode)
	elseif key == "v" then
		if Scene.camera.mode == "ortho" then
			Scene.camera.params.ortho_size = (Scene.camera.params.ortho_size or 10) + 1
			Scene.camera:update_projection()
		end
	elseif key == "b" then
		if Scene.camera.mode == "ortho" then
			Scene.camera.params.ortho_size = math.max(1, (Scene.camera.params.ortho_size or 10) - 1)
			Scene.camera:update_projection()
		end
	end
end
