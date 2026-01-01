-- main.lua
local model_mesh = nil
local floor_mesh = nil
local voxels = {}
local palette = {}

-- Camera
local cam = { rot_x = 0.6, rot_y = 0.8, zoom = 60 }

-- Shader with simple lighting
local shader_code = [[
    varying vec3 v_normal;
    varying vec4 v_color;

    #ifdef VERTEX
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    attribute vec3 VertexNormal;

    vec4 position(mat4 transform_projection, vec4 vertex_position) {
        v_normal = (model * vec4(VertexNormal, 0.0)).xyz;
        v_color = VertexColor;
        return projection * view * model * vertex_position;
    }
    #endif

    #ifdef PIXEL
    vec4 effect(vec4 color, Image tex, vec2 tex_coords, vec2 screen_coords) {
        vec3 light_dir = normalize(vec3(0.5, 1.0, 0.3));
        float diff = max(dot(normalize(v_normal), light_dir), 0.0);
        float ambient = 0.3;
        return v_color * (diff + ambient);
    }
    #endif
]]

local shader = nil

function love.load(args)
    love.window.setTitle("LÖVE Vox Viewer")
    love.window.setMode(800, 600, {resizable=true, depth=24})
    love.graphics.setDepthMode("lequal", true)
    shader = love.graphics.newShader(shader_code)

    local filename = "chair.vox"
    for i, arg in ipairs(args) do if arg:match("%.vox$") then filename = arg end end
    if love.filesystem.getInfo(filename) then load_vox(filename) end
    
    -- Ground plane
    local f_verts = {
        {-100, 0, -100, 0,1,0, 0.2, 0.2, 0.2, 1},
        { 100, 0, -100, 0,1,0, 0.2, 0.2, 0.2, 1},
        { 100, 0,  100, 0,1,0, 0.2, 0.2, 0.2, 1},
        {-100, 0, -100, 0,1,0, 0.2, 0.2, 0.2, 1},
        { 100, 0,  100, 0,1,0, 0.2, 0.2, 0.2, 1},
        {-100, 0,  100, 0,1,0, 0.2, 0.2, 0.2, 1},
    }
    local format = {{"VertexPosition", "float", 3}, {"VertexNormal", "float", 3}, {"VertexColor", "float", 4}}
    floor_mesh = love.graphics.newMesh(format, f_verts, "triangles")
end

function load_vox(filename)
    local data = love.filesystem.newFileData(filename)
    local pointer = 0
    local function read_str(len) local s = love.data.unpack("<c"..len, data, pointer+1); pointer = pointer+len; return s end
    local function read_u32() local n = love.data.unpack("<I4", data, pointer+1); pointer = pointer+4; return n end
    local function read_u8() local n = love.data.unpack("<I1", data, pointer+1); pointer = pointer+1; return n end

    read_str(4) -- Header
    read_u32()  -- Version

    voxels = {}
    palette = {}
    for i=1, 256 do palette[i] = {1, 1, 1, 1} end

    while pointer + 12 <= data:getSize() do
        local id = read_str(4)
        local c_size = read_u32()
        local ch_size = read_u32()
        local next_p = pointer + c_size + ch_size
        
        if id == "XYZI" then
            local n = read_u32()
            for i=1, n do
                local x = read_u8()
                local y = read_u8()
                local z = read_u8()
                local c = read_u8()
                table.insert(voxels, {x=x, y=y, z=z, c=c})
            end
            pointer = next_p
        elseif id == "RGBA" then
            local num_colors = math.floor(c_size / 4)
            for i=1, num_colors do
                local r = read_u8()
                local g = read_u8()
                local b = read_u8()
                local a = read_u8()
                palette[i] = {r/255, g/255, b/255, a/255}
            end
            pointer = next_p
        elseif id == "MAIN" then
            -- Container chunk, don't jump to next_p, just enter it.
        else
            pointer = next_p
        end
    end
    create_mesh()
end

function create_mesh()
    local vertices = {}
    local offsets = {{0,0,0},{1,0,0},{1,1,0},{0,1,0},{0,0,1},{1,0,1},{1,1,1},{0,1,1}}
    local faces = {
        {1,2,3,4, 0,0,-1}, {5,8,7,6, 0,0,1}, {1,5,6,2, 0,-1,0},
        {4,3,7,8, 0,1,0},  {1,4,8,5, -1,0,0}, {2,6,7,3, 1,0,0}
    }
    
    local min_x, max_x, min_y, max_y, min_z, max_z = 1000,-1000,1000,-1000,1000,-1000
    for _, v in ipairs(voxels) do
        min_x = math.min(min_x, v.x); max_x = math.max(max_x, v.x)
        min_y = math.min(min_y, v.y); max_y = math.max(max_y, v.y)
        min_z = math.min(min_z, v.z); max_z = math.max(max_z, v.z)
    end
    local cx, cy, cz = (min_x+max_x+1)/2, (min_y+max_y+1)/2, (min_z+max_z+1)/2

    for _, v in ipairs(voxels) do
        local col = palette[v.c] or {1,0,1,1}
        local vx, vy, vz = v.x-cx, v.z-cz, v.y-cy -- Map Z to Y-up
        for _, f in ipairs(faces) do
            local function p(i)
                local o = offsets[f[i]]
                table.insert(vertices, {vx+o[1], vz+o[3], vy+o[2], f[5],f[7],f[6], col[1],col[2],col[3],col[4]})
            end
            p(1); p(2); p(3); p(1); p(3); p(4)
        end
    end
    
    if #vertices > 0 then
        local format = {{"VertexPosition", "float", 3}, {"VertexNormal", "float", 3}, {"VertexColor", "float", 4}}
        model_mesh = love.graphics.newMesh(format, vertices, "triangles")
    end
end

function love.update(dt)
    local k = love.keyboard
    if k.isDown("r") then cam.rot_x, cam.rot_y, cam.zoom = 0.6, 0.8, 60 end
    if k.isDown("left") or k.isDown("a") then cam.rot_y = cam.rot_y - 2*dt end
    if k.isDown("right") or k.isDown("d") then cam.rot_y = cam.rot_y + 2*dt end
    if k.isDown("up") or k.isDown("w") then cam.rot_x = cam.rot_x - 2*dt end
    if k.isDown("down") or k.isDown("s") then cam.rot_x = cam.rot_x + 2*dt end
    if k.isDown("q") then cam.zoom = cam.zoom - 40*dt end
    if k.isDown("e") then cam.zoom = cam.zoom + 40*dt end
end

local function mult(a, b)
    local c = {}
    for i=0,3 do for j=0,3 do local s = 0
        for k=0,3 do s = s + a[k*4+j+1] * b[i*4+k+1] end
        c[i*4+j+1] = s
    end end
    return c
end

function love.draw()
    love.graphics.clear({0.1, 0.1, 0.15, 1.0}, true, true)
    local w, h = love.graphics.getDimensions()
    local t = math.tan(math.rad(60)/2)
    local aspect = w/h
    local f, n = 1000, 0.1
    local projection = {1/(t*aspect),0,0,0, 0,1/t,0,0, 0,0,-(f+n)/(f-n),-1, 0,0,-2*f*n/(f-n),0}
    
    local view = {1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,-cam.zoom,1}
    local cx, sx = math.cos(cam.rot_x), math.sin(cam.rot_x)
    local cy, sy = math.cos(cam.rot_y), math.sin(cam.rot_y)
    view = mult(view, {1,0,0,0, 0,cx,sx,0, 0,-sx,cx,0, 0,0,0,1})
    view = mult(view, {cy,0,-sy,0, 0,1,0,0, sy,0,cy,0, 0,0,0,1})

    love.graphics.setShader(shader)
    shader:send("projection", projection)
    shader:send("view", view)
    
    shader:send("model", {1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1})
    if floor_mesh then love.graphics.draw(floor_mesh) end
    if model_mesh then love.graphics.draw(model_mesh) end
    love.graphics.setShader()

    love.graphics.setColor(1, 1, 1, 0.8)
    love.graphics.print("Arrows/WASD: Orbit", 10, 10)
    love.graphics.print("Q/E or Wheel: Zoom", 10, 30)
    love.graphics.print("R: Reset Camera", 10, 50)
end
