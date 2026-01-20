local scene_path = ...

if not scene_path then
    print("Usage: lua visualize_scene.lua <path_to_scene.lua>")
    return
end

-- Determine output path (replace .lua with .txt)
local out_path = scene_path:gsub("%.lua$", ".txt")
if out_path == scene_path then out_path = scene_path .. ".txt" end

-- Load the scene
local chunk, err = loadfile(scene_path)
if not chunk then
    print("Error loading scene:", err)
    return
end

local scene = chunk()

if not scene or not scene.tiles then
    print("Error: Scene file did not return a table with a 'tiles' field.")
    return
end

-- Helper to collect output
local output = {}
local function log(str)
    table.insert(output, str)
    print(str) -- Also print to stdout
end

-- Process tiles
local grid = {}
local min_x, max_x = 0, 0
local min_y, max_y = 0, 0

local legend = {}
local next_char_idx = 1
local chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
local id_to_char = {}

for _, tile in ipairs(scene.tiles) do
    local x, y = tile.pos[1], tile.pos[2]
    local z = tile.pos[3] or 0
    local id = tile.tile_id
    local unique_key = id .. ":" .. z
    
    if x < min_x then min_x = x end
    if x > max_x then max_x = x end
    if y < min_y then min_y = y end
    if y > max_y then max_y = y end
    
    if not id_to_char[unique_key] then
        if next_char_idx > #chars then
            id_to_char[unique_key] = "?"
        else
            local char = chars:sub(next_char_idx, next_char_idx)
            id_to_char[unique_key] = char
            legend[char] = {id=id, height=z}
            next_char_idx = next_char_idx + 1
        end
    end
    
    if not grid[y] then grid[y] = {} end
    grid[y][x] = id_to_char[unique_key]
end

log("Layout: " .. scene_path)
log("Range: (" .. min_x .. "," .. min_y .. ") to (" .. max_x .. "," .. max_y .. ")")
log("Legend:")
local sorted_legend = {}
for char, info in pairs(legend) do
    table.insert(sorted_legend, {char=char, id=info.id, height=info.height})
end
table.sort(sorted_legend, function(a,b) return a.char < b.char end)

for _, item in ipairs(sorted_legend) do
    log("  " .. item.char .. ": " .. item.id .. " (H=" .. item.height .. ")")
end

log("\nGrid (North ^ [-Z]):")
log("       North (Back Wall)")
log("         ^")

-- Loop from min_y (North/Top) to max_y (South/Bottom)
for y = min_y, max_y do
    local row_label = string.format("%2d | ", y)
    local row_str = ""
    for x = min_x, max_x do
        local char = (grid[y] and grid[y][x]) or "."
        row_str = row_str .. " " .. char
    end
    -- Add "West" label on the left side for the middle row (approx)
    if y == math.floor((min_y + max_y) / 2) then
        row_str = " West (Back Wall) < " .. row_label .. row_str .. " > East (Front)"
    else
        row_str = "                   " .. row_label .. row_str
    end
    log(row_str)
end

log("         v")
log("       South (Front/Camera)")

-- Add Column Numbering
local col_header = "          "
local col_divider = "          "
for x = min_x, max_x do
    col_header = col_header .. string.format(" %X", x % 16) -- Use Hex for single-char numbering
    col_divider = col_divider .. "--"
end
log(col_divider)
log(col_header)

-- Save to file
local f = io.open(out_path, "w")
if f then
    f:write(table.concat(output, "\n"))
    f:close()
    print("\nSaved layout to: " .. out_path)
else
    print("\nError: Could not save to " .. out_path)
end