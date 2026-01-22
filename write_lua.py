lua_code = r"""local ascii_loader = {}

local function parse_props(s)
    local props = {}
    if not s then return props end
    for k, v in s:gmatch("(%w+)=([^,%s}]+)") do
        local n = tonumber(v)
        props[k] = n or v
    end
    return props
end

function ascii_loader.load(path)
    local info = love.filesystem.getInfo(path)
    if not info then return nil, "File not found: " .. path end

    local legend = {}
    local grid = {}
    local current_section = nil
    local dir = path:match("(.-)[^/]+$") or ""

    for line in love.filesystem.lines(path) do
        line = line:gsub("^%s*(.-)%s*$", "%1")
        if line ~= "" and line:sub(1, 2) ~= "//" then
            local is_comment = line:sub(1, 1) == "#" and not line:find("=")
            if not is_comment then
                if line:find("^THEME%s*=") then
                    local t_path = line:match("=%s*(.-)%s*$")
                    if not love.filesystem.getInfo(t_path) then
                        t_path = dir .. t_path
                    end
                    if love.filesystem.getInfo(t_path) then
                        local t_legend = ascii_loader.load_legend_only(t_path)
                        for k, v in pairs(t_legend) do legend[k] = v end
                    else
                        print("Warning: Could not find theme file: " .. t_path)
                    end
                elseif line == "LEGEND" then current_section = "LEGEND"
                elseif line == "GRID" then current_section = "GRID"
                elseif current_section == "LEGEND" then
                    local key, tid, props_s = line:match("^(%S+)%s*=%s*([^%s{]+)%s*(.*)$")
                    if key and tid then
                        legend[key] = { tile_id = tid, props = parse_props(props_s) }
                    end
                elseif current_section == "GRID" then
                    local row = {}
                    for word in line:gmatch("%S+") do table.insert(row, word) end
                    table.insert(grid, row)
                end
            end
        end
    end

    local tiles = {}
    for z, row in ipairs(grid) do
        for x, key in ipairs(row) do
            local item_info = legend[key]
            local rot_off = 0
            if not item_info and #key > 1 then
                local base, digit = key:match("^(.-)(%d)$")
                local d = tonumber(digit)
                if base and legend[base] and d and d >= 0 and d <= 3 then
                    item_info = legend[base]
                    rot_off = d * 90
                end
            end
            if item_info and item_info.tile_id:upper() ~= "SKIP" then
                local rot = (item_info.props.rot or 0) + rot_off
                table.insert(tiles, {
                    tile_id = item_info.tile_id,
                    pos = { x - 1, z - 1 },
                    rot = rot,
                    height = item_info.props.height or 0
                })
            end
        end
    end
    return {
        tiles = tiles,
        layout = {},
        ambientColor = { 0.2, 0.2, 0.3 },
        ambientIntensity = 1.0,
        dirLightDirection = { 0.5, -1.0, 0.5 },
        dirLightColor = { 0.7, 0.7, 0.9 },
        fogColor = { 0.1, 0.1, 0.15 },
        fogNear = 200,
        fogFar = 800
    }
end

function ascii_loader.load_legend_only(path)
    local legend = {}
    local current_section = nil
    for line in love.filesystem.lines(path) do
        line = line:gsub("^%s*(.-)%s*$", "%1")
        if line ~= "" and line:sub(1, 2) ~= "//" then
            local is_comment = line:sub(1, 1) == "#" and not line:find("=")
            if not is_comment then
                if line == "LEGEND" then current_section = "LEGEND"
                elseif current_section == "LEGEND" then
                    local key, tid, props_s = line:match("^(%S+)%s*=%s*([^%s{]+)%s*(.*)$")
                    if key and tid then
                        legend[key] = { tile_id = tid, props = parse_props(props_s) }
                    end
                end
            end
        end
    end
    return legend
end

return ascii_loader
"""

with open("/home/aaron-ma/love_exp/ascii_loader.lua", "w") as f:
    f.write(lua_code)