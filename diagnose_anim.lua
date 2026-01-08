
local json = require("sprite_to_3d.preview_v2.json")

local function read_json(path)
    local f = io.open(path, "r")
    if not f then return nil end
    local content = f:read("*all")
    f:close()
    return json.decode(content)
end

local anim = read_json("sprite_to_3d/preview_v2/hero_anim.json")
local rig = read_json("sprite_to_3d/preview_v2/hero_rigged.json")

print("Anim Type:", anim.type)
print("Frame Count:", anim.duration)

local bone_name = "mixamorig_Hips"
local parent_name = "mixamorig_Spine" -- actually Hips is parent of Spine

if anim.frames and anim.frames[1] then
    local frame = anim.frames[1]
    local d = frame[bone_name]
    if d then
        print("\nHips Matrix (Frame 1):")
        print(string.format("[ %0.2f, %0.2f, %0.2f, %0.2f ]", d[1], d[2], d[3], d[4]))
        print(string.format("[ %0.2f, %0.2f, %0.2f, %0.2f ]", d[5], d[6], d[7], d[8]))
        print(string.format("[ %0.2f, %0.2f, %0.2f, %0.2f ]", d[9], d[10], d[11], d[12]))
        print(string.format("[ %0.2f, %0.2f, %0.2f, %0.2f ]", d[13], d[14], d[15], d[16]))
        
        print("\nRow-Major Interpretation (Last Col):", d[4], d[8], d[12])
        print("Column-Major Interpretation (Last Row):", d[13], d[14], d[15])
    end
    
    local d2 = frame["mixamorig_RightUpLeg"]
    if d2 then
        print("\nRightUpLeg Matrix (Frame 1):")
        print(string.format("[ %0.2f, %0.2f, %0.2f, %0.2f ]", d2[1], d2[2], d2[3], d2[4]))
        print(string.format("[ %0.2f, %0.2f, %0.2f, %0.2f ]", d2[5], d2[6], d2[7], d2[8]))
        print(string.format("[ %0.2f, %0.2f, %0.2f, %0.2f ]", d2[9], d2[10], d2[11], d2[12]))
        print(string.format("[ %0.2f, %0.2f, %0.2f, %0.2f ]", d2[13], d2[14], d2[15], d2[16]))
    end
end

local rp = rig.skeleton.rest_pose
print("\nRest Pose Hips:", rp[bone_name][1], rp[bone_name][2], rp[bone_name][3])
print("Rest Pose RightUpLeg:", rp["mixamorig_RightUpLeg"][1], rp["mixamorig_RightUpLeg"][2], rp["mixamorig_RightUpLeg"][3])

