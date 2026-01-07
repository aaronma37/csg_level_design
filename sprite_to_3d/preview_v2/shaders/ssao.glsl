#pragma language glsl3

uniform sampler2D depthTex;
uniform sampler2D normalTex;
uniform sampler2D noiseTex;

uniform vec3 samples[64];
uniform mat4 projection;
uniform vec2 noiseScale;

uniform float radius = 0.5;
uniform float bias = 0.025;

// Parameters for reconstructing view-space position
uniform float near = 0.5;
uniform float far = 1024.0;
uniform vec2 screenSize;

vec3 getViewPos(vec2 texCoord) {
    float depth = Texel(depthTex, texCoord).r;
    // Assuming depth is already view-space depth from our normal_depth shader
    
    // We need to reconstruct X and Y from screen coordinates and view depth
    // This depends on the projection matrix.
    // For a standard perspective projection:
    // x = (2.0 * texCoord.x - 1.0) * depth * (aspect * tan(fov/2))
    // y = (2.0 * texCoord.y - 1.0) * depth * tan(fov/2)
    
    // A more general way if we have the inverse projection:
    // but we can also use the projection matrix entries.
    float invP00 = 1.0 / projection[0][0];
    float invP11 = 1.0 / projection[1][1];
    
    vec3 viewPos;
    viewPos.z = -depth;
    viewPos.x = (texCoord.x * 2.0 - 1.0) * invP00 * depth;
    viewPos.y = (1.0 - texCoord.y * 2.0) * invP11 * depth;
    // Note: LÖVE/Menori might have Y flipped, we'll check later.
    return viewPos;
}

vec4 effect(vec4 color, Image tex, vec2 texCoord, vec2 screen_coords) {
    vec3 fragPos = getViewPos(texCoord);
    vec3 normal = normalize(Texel(normalTex, texCoord).xyz * 2.0 - 1.0);
    vec3 randomVec = normalize(Texel(noiseTex, texCoord * noiseScale).xyz);
    
    vec3 tangent = normalize(randomVec - normal * dot(randomVec, normal));
    vec3 bitangent = cross(normal, tangent);
    mat3 TBN = mat3(tangent, bitangent, normal);
    
    float occlusion = 0.0;
    for(int i = 0; i < 64; ++i) {
        // From tangent to view-space
        vec3 samplePos = TBN * samples[i];
        samplePos = fragPos + samplePos * radius;
        
        // Project sample position to find corresponding texture coordinate
        vec4 offset = projection * vec4(samplePos, 1.0);
        offset.xyz /= offset.w;
        offset.x = offset.x * 0.5 + 0.5;
        offset.y = (offset.y - 1.0) / -2.0; // Map NDC Y to [0, 1] with flip
        
        float sampleDepth = Texel(depthTex, offset.xy).r;
        
        float rangeCheck = smoothstep(0.0, 1.0, radius / abs(fragPos.z + sampleDepth));
        occlusion += (sampleDepth <= -samplePos.z + bias ? 1.0 : 0.0) * rangeCheck;
    }
    
    occlusion = 1.0 - (occlusion / 64.0);
    return vec4(vec3(occlusion), 1.0);
}
