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
    cam_angle = 0,
    cam_dist = 60,
    cam_height = 15,
    cam_center = vec3(0, 10, 0),
}

function App:load()
    love.graphics.setDefaultFilter("nearest", "nearest")
    
    -- 1. Shader
    local vertex_code = [[ 
        attribute vec3 VertexNormal;
        uniform mat4 m_projection;
        uniform mat4 m_view;
        uniform mat4 m_model;
        varying vec3 v_normal;
        varying vec4 v_color;
        varying vec2 v_texcoord;
        vec4 position(mat4 transform_projection, vec4 vertex_position) {
            v_normal = normalize(mat3(m_model) * VertexNormal);
            v_color = VertexColor;
            v_texcoord = VertexTexCoord.xy;
            return m_projection * m_view * m_model * vertex_position;
        }
    ]]
    local pixel_code = [[
        varying vec3 v_normal;
        varying vec4 v_color;
        varying vec2 v_texcoord;
        uniform bool unlit;
        vec4 effect(vec4 color, Image tex, vec2 texture_coords, vec2 screen_coords) {
            vec4 texColor = Texel(tex, v_texcoord);
            if (texColor.a < 0.1) discard;
            if (unlit) return texColor * v_color * color;
            float diff = max(dot(v_normal, normalize(vec3(0.5, 1.0, 0.5))), 0.0);
            return texColor * v_color * color * (0.3 + diff * 0.7);
        }
    ]]
    
    self.shader = love.graphics.newShader(vertex_code, pixel_code)

    self.palette = love.graphics.newImage("assets/palette_texture.png")
    
    -- 2. Load Data
    local f = io.open(RIG_PATH, "r")
    if f then
        self.rig_data = json.decode(f:read("*all"))
        f:close()
    end
    
    f = io.open(ANIM_PATH, "r")
    if f then
        self.anim_data = json.decode(f:read("*all"))
        f:close()
    end

    -- 3. Setup Scene
    self.scene = menori.Scene()
    self.root = menori.Node()
    self.camera = menori.Camera3D("perspective", { fov = 30 })
    self.env = menori.Environment(self.camera)
    
    self.camera.eye = vec3(0, 15, 60)
    self.camera.center = self.cam_center
    self.camera:update_projection()
    self.camera:update_view_matrix()

    -- 4. Character
    if self.rig_data then
        self.char_root = menori.Node()
        self.root:attach(self.char_root)
        self:build_skeleton(self.char_root)
    end
end

function App:build_voxel_mesh(voxels)
    local vertices = {}
    local format = {
        {"VertexPosition", "float", 3},
        {"VertexNormal", "float", 3},
        {"VertexColor", "float", 4},
        {"VertexTexCoord", "float", 2},
    }
    
    for _, v in ipairs(voxels) do
        local vx, vy, vz, c = v[1], v[2], v[3], v[4]
        local u = (c + 0.5) / 256.0
        local x, y, z = vx, vy, vz -- Use consistent Y-up
        local faces = {
            {n={0,1,0}, v={{0,1,0}, {1,1,0}, {1,1,1}, {0,1,1}}},
            {n={0,-1,0}, v={{0,0,1}, {1,0,1}, {1,0,0}, {0,0,0}}},
            {n={0,0,1}, v={{0,0,1}, {1,0,1}, {1,1,1}, {0,1,1}}},
            {n={0,0,-1}, v={{1,0,0}, {0,0,0}, {0,1,0}, {1,1,0}}},
            {n={1,0,0}, v={{1,0,0}, {1,0,1}, {1,1,1}, {1,1,0}}},
            {n={-1,0,0}, v={{0,0,1}, {0,0,0}, {0,1,0}, {0,1,1}}},
        }
        for _, f in ipairs(faces) do
            for _, i in ipairs({1, 2, 3, 1, 3, 4}) do
                local vert = f.v[i]
                table.insert(vertices, {
                    x + vert[1], y + vert[2], z + vert[3],
                    f.n[1], f.n[2], f.n[3],
                    1, 1, 1, 1,
                    u, 0.5
                })
            end
        end
    end
    return menori.Mesh({vertices = vertices, vertexformat = format})
end

function App:build_skeleton(parent_node)
    self.bones = {}
    local topology = self.rig_data.skeleton.topology
    local rest_pose = self.rig_data.skeleton.rest_pose
    local parts = self.rig_data.parts
    
    for bone_name, _ in pairs(rest_pose) do
        self.bones[bone_name] = menori.Node()
    end
    
    for bone_name, parent_name in pairs(topology) do
        local node = self.bones[bone_name]
        local bp = rest_pose[bone_name]
        
        if parent_name and self.bones[parent_name] then
            self.bones[parent_name]:attach(node)
        else
            parent_node:attach(node)
        end
        
        if parts[bone_name] and #parts[bone_name].voxels > 0 then
            local mesh = self:build_voxel_mesh(parts[bone_name].voxels)
            local mat = menori.Material()
            mat.main_texture = self.palette
            if self.shader then mat:set_shader(self.shader) end
            mat.mesh_cull_mode = "none"
            node:attach(menori.ModelNode(mesh, mat))
        end
    end
end

function App:update(dt)
    if love.keyboard.isDown("left") then self.cam_angle = self.cam_angle - dt end
    if love.keyboard.isDown("right") then self.cam_angle = self.cam_angle + dt end
    
    self.camera.eye.x = math.cos(self.cam_angle) * self.cam_dist
    self.camera.eye.z = math.sin(self.cam_angle) * self.cam_dist
    self.camera:update_view_matrix()
    
    if self.anim_data then
        self.time = self.time + dt
        local frame_idx = math.floor(self.time * self.animation_speed) % self.anim_data.duration
        local frame = self.anim_data.frames[frame_idx + 1]
        
        for bone_name, m_data in pairs(frame) do
            local node = self.bones[bone_name]
            if node then
                -- DAE is row-major, Menori is column-major. Transpose while loading.
                local m = ml.mat4(
                    m_data[1], m_data[5], m_data[9], m_data[13],
                    m_data[2], m_data[6], m_data[10], m_data[14],
                    m_data[3], m_data[7], m_data[11], m_data[15],
                    m_data[4], m_data[8], m_data[12], m_data[16]
                )
                node.local_matrix = m
                node._transform_flag = true
            end
        end
    end
end

function App:draw()
    love.graphics.clear(0.1, 0.1, 0.12, 1, true, true)
    
    if self.shader then
        local proj = self.camera.m_projection:clone()
        proj[6] = -proj[6] 
        self.shader:send("m_view", "column", self.camera.m_view.data)
        self.shader:send("m_projection", "column", proj.data)
        self.shader:send("unlit", true)
    end

    self.scene:update_nodes(self.root, self.env)
    self.scene:render_nodes(self.root, self.env)
    
    love.graphics.setShader()
    love.graphics.setColor(1, 1, 1)
    love.graphics.print("Rigged Preview (V_TEXCOORD FIXED)", 10, 10)
end

function love.load() App:load() end
function love.update(dt) App:update(dt) end
function love.draw() App:draw() end
