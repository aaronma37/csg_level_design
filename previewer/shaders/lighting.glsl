#pragma language glsl3

#ifdef VERTEX
uniform mat4 m_projection;
uniform mat4 m_view;
uniform mat4 m_model;
// uniform bool isCanvasEnabled; // Menori handles Y-flip in projection

attribute vec3 VertexNormal;

varying vec4 worldPosition;
varying vec4 viewPosition;
varying vec4 screenPosition;
varying vec3 vertexNormal;
varying vec4 vertexColor;
varying vec3 objectPosition;
varying vec3 objectNormal;

vec4 position(mat4 transformProjection, vec4 vertexPosition) {
    worldPosition = m_model * vertexPosition;
    viewPosition = m_view * worldPosition;
    screenPosition = m_projection * viewPosition;
    
    objectPosition = vertexPosition.xyz;
    objectNormal = VertexNormal;
    
    // Transform normal to world space
    vertexNormal = normalize(mat3(m_model) * VertexNormal);
    vertexColor = VertexColor;

    return screenPosition;
}
#endif

#ifdef PIXEL
varying vec4 worldPosition;
varying vec4 viewPosition;
varying vec4 screenPosition;
varying vec3 vertexNormal;
varying vec4 vertexColor;
varying vec3 objectPosition;
varying vec3 objectNormal;

uniform vec3 ambientColor;
uniform float ambientIntensity;
uniform vec3 dirLightDirection;
uniform vec3 dirLightColor;

uniform vec3 eyePosition;

uniform bool showIndices;
uniform float isProcedural;

uniform sampler2D ssaoTex;
uniform sampler2D shadowMap;
uniform mat4 lightSpaceMatrix;

uniform vec3 fogColor;
uniform float fogNear;
uniform float fogFar;

#define MAX_LIGHTS 16
uniform int numLights;
uniform vec3 lightPositions[MAX_LIGHTS];
uniform vec3 lightColors[MAX_LIGHTS];
uniform float lightIntensities[MAX_LIGHTS]; // Radius/Range

uniform bool unlit;

// Noise functions for procedural materials
float hash3(vec3 p) {
    p = fract(p * 0.1031);
    p += dot(p, p.zyx + 31.32);
    return fract((p.x + p.y) * p.z);
}

float noise(vec3 x) {
    vec3 i = floor(x);
    vec3 f = fract(x);
    vec3 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(hash3(i + vec3(0,0,0)), hash3(i + vec3(1,0,0)), u.x),
                   mix(hash3(i + vec3(0,1,0)), hash3(i + vec3(1,1,0)), u.x), u.y),
               mix(mix(hash3(i + vec3(0,0,1)), hash3(i + vec3(1,0,1)), u.x),
                   mix(hash3(i + vec3(0,1,1)), hash3(i + vec3(1,1,1)), u.x), u.y), u.z);
}

vec4 effect(vec4 color, Image tex, vec2 texture_coords, vec2 screen_coords) {
    if (showIndices) {
        int idx = int(floor(texture_coords.x * 255.0));
        if (idx <= 20) return vec4(1.0, 0.0, 0.0, 1.0); // Wood = Red
        if (idx > 20 && idx <= 40) return vec4(0.0, 1.0, 0.0, 1.0); // Stone = Green
        if (idx >= 250) return vec4(1.0, 1.0, 0.0, 1.0); // Ghost = Yellow
        if (idx >= 240) return vec4(0.0, 0.0, 1.0, 1.0); // Emissive = Blue
        return vec4(vec3(float(idx) / 255.0), 1.0); // Others = Grayscale
    }

    vec4 texColor = Texel(tex, texture_coords);
    
    // Discard transparent pixels
    if (texColor.a < 0.1) discard;

    vec3 normal = normalize(vertexNormal);
    
    // Material System based on Palette Index
    int matIndex = int(floor(texture_coords.x * 255.0));
    vec3 albedo = texColor.rgb;
    
    // Default Material Properties
    float specIntensity = 0.0;
    float shininess = 32.0;

    if (isProcedural > 0.5 && matIndex <= 20) {
        // Procedural Wood
        albedo *= 2.0;

        // --- TUNEABLE PARAMETERS ---
        float texRes = 1.0;         // Virtual resolution (pixels per meter)
        float grainScale = 45.0;     // Frequency of the main grain
        float normalStrength = 10.0;// Height of the normal map bumps
        float lodFadeStart = 0.6;    // LOD fading start (lower = fades closer)
        float lodFadeEnd = 0.1;      // LOD fading end
        float aaSoftness = 3.5;      // Width of AA transitions (1.0 = sharp)
        // ---------------------------

        vec3 p_raw = objectPosition;
        vec3 v = p_raw * texRes;
        vec3 f = fract(v);
        vec3 fw_snap = fwidth(v);
        vec3 snap_blend = smoothstep(0.5 - fw_snap * aaSoftness, 0.5 + fw_snap * aaSoftness, f);
        vec3 p = (floor(v) + snap_blend - 0.5) / texRes;
        
        vec3 n_obj = normalize(objectNormal);
        vec3 absN = abs(n_obj);
        
        // Plank Logic
        float plankWidth = 0.4;
        float plankCoordRaw = (absN.y > 0.5) ? p_raw.x : ((absN.x > 0.5) ? p_raw.z : p_raw.x);
        plankCoordRaw /= plankWidth;
        
        float plankId = floor(plankCoordRaw);
        float plankOffset = hash3(vec3(plankId, matIndex, 0.0)) * 10.0;
        
        // Anti-aliased plank gaps
        float edge = fract(plankCoordRaw);
        float fw_p = fwidth(plankCoordRaw);
        float gapMask = smoothstep(0.0, fw_p * aaSoftness, edge) * (1.0 - smoothstep(1.0 - 0.03 - fw_p * aaSoftness, 1.0 - 0.03, edge));
        
        if (absN.y > 0.5) {
            p.z += plankOffset;
            p.x += hash3(vec3(plankId, 0.1, 0.0)) * 0.1;
        } else {
            p.y += plankOffset;
        }

        p += float(matIndex) * 2.0;

        // Moiré Suppression via frequency-based clamping
        vec3 fw_p_vec = fwidth(p_raw);
        float grainLOD = smoothstep(lodFadeStart, lodFadeEnd, length(fw_p_vec * grainScale));
        float fiberLOD = smoothstep(lodFadeStart, lodFadeEnd, length(fw_p_vec * grainScale * 2.0));

        float sideMix = 1.0;
        if (absN.y < 0.5) {
            sideMix = 0.0;
        }
        
        float g1 = noise(p * vec3(grainScale, grainScale, 0.5));
        float g2 = noise(p * vec3(grainScale * 0.33, grainScale * 0.33, 0.1));
        float grainRaw = mix(0.5, g1 * 0.7 + g2 * 0.3, sideMix);
        
        // Analytic Anti-Aliasing for Grain
        float g_fw = fwidth(grainRaw);
        float grainAA = clamp((grainRaw - 0.5) / max(g_fw * aaSoftness, 0.001) + 0.5, 0.0, 1.0);
        float finalGrain = mix(0.5, grainAA, grainLOD);
        
        // Roughness
        float woodRoughness = mix(0.2, 0.6, smoothstep(0.1, 0.5, grainRaw));
        woodRoughness = mix(1.0, woodRoughness, gapMask);
        float roughNoise = noise(p * 200.0);
        // Dampen high-freq roughness noise on sides to reduce graininess
        float roughnessDetail = (roughNoise * 0.25 - 0.1) * fiberLOD;
        if (absN.y < 0.5) roughnessDetail *= 0.1; // 90% reduction on sides
        
        woodRoughness = clamp(woodRoughness + roughnessDetail, 0.0, 1.0);
        
        specIntensity = mix(0.25, 0.02, woodRoughness) * gapMask;
        if (matIndex >= 15) specIntensity *= 2.5; 
        shininess = mix(50.0, 2.0, woodRoughness);

        // Normal Mapping (Derivative-Based)
        float hValue = (grainRaw * 0.4 + gapMask * 0.6) * normalStrength * grainLOD;
        vec3 dpdx = dFdx(worldPosition.xyz);
        vec3 dpdy = dFdy(worldPosition.xyz);
        vec3 r1 = cross(dpdy, normal);
        vec3 r2 = cross(normal, dpdx);
        float det = dot(dpdx, r1);
        if (abs(det) > 1e-9) {
            vec3 surfGrad = (dFdx(hValue) * r1 + dFdy(hValue) * r2) / det;
            normal = normalize(normal - surfGrad);
        }
        
        // Final Albedo Modulation
        float contrast = 0.001 + mod(float(matIndex), 3.0) * 0.05;
        vec3 darkWood = albedo * (1.0 - contrast);
        albedo = mix(albedo, darkWood, finalGrain * 0.5);
        albedo *= mix(0.4, 1.0, gapMask);
        
        float variation = hash3(vec3(plankOffset, 123.4, 0.0));
        albedo *= (0.9 + 0.25 * variation);

        // Posterization - DISABLED for DEBUG
        // float levels = 12.0;
        // albedo = floor(albedo * levels + 0.5) / levels;
    } else if (isProcedural > 0.5 && matIndex > 20 && matIndex <= 40) {
        // Procedural Stone
        vec3 p_raw = objectPosition;
        float texRes = 128.0;
        vec3 v = p_raw * texRes;
        vec3 f = fract(v);
        vec3 fw_snap = fwidth(v);
        vec3 snap_blend = smoothstep(0.4, 0.6, f); // Slightly sharper snapping for stone
        vec3 p = (floor(v) + snap_blend - 0.5) / texRes;

        // Color Mottling (Extremely Low Frequency)
        float noise1 = noise(p * 0.1);
        float noise2 = noise(p * 0.3);
        float mottling = noise1 * 0.7 + noise2 * 0.3;
        
        // Base color variation based on material index
        float varScale = 0.1 + mod(float(matIndex), 5.0) * 0.05;
        albedo *= (1.0 - varScale * 0.5 + mottling * varScale);

        // Roughness (Stone is very matte)
        float stoneRoughness = 0.95 + noise(p * 40.0) * 0.05;
        stoneRoughness = clamp(stoneRoughness, 0.0, 1.0);
        
        specIntensity = 0.0;
        shininess = 1.0;

        // Bumpy Normal Mapping (Derivative-Based)
        float stoneLOD = smoothstep(0.8, 0.1, length(fwidth(p_raw * 40.0)));
        float hValue = mottling * 0.008 * stoneLOD;
        vec3 dpdx = dFdx(worldPosition.xyz);
        vec3 dpdy = dFdy(worldPosition.xyz);
        vec3 r1 = cross(dpdy, normal);
        vec3 r2 = cross(normal, dpdx);
        float det = dot(dpdx, r1);
        if (abs(det) > 1e-9) {
            vec3 surfGrad = (dFdx(hValue) * r1 + dFdy(hValue) * r2) / det;
            normal = normalize(normal - surfGrad);
        }

        // Posterization
        float levels = 8.0; // Slightly more quantized for stone
        albedo = floor(albedo * levels + 0.5) / levels;
    }

    vec2 screenUV = screen_coords.xy / love_ScreenSize.xy;
    float ao = Texel(ssaoTex, screenUV).r;
    // Make AO less aggressive so it doesn't completely black out areas
    ao = mix(0.15, 1.0, ao);
    
    vec3 viewDir = normalize(eyePosition - worldPosition.xyz);
    
    // Ambient lighting with AO
    vec3 lighting = (ambientColor * ambientIntensity) * ao;
    
    // Add a tiny bit of "fake" hemisphere light to keep things from being purely flat in the shade
    float hemi = normal.y * 0.5 + 0.5;
    lighting += ambientColor * ambientIntensity * hemi * 0.1;
    
    // Directional Light
    vec3 dirLightDirNorm = normalize(-dirLightDirection);
    float dirDiff = max(dot(normal, dirLightDirNorm), 0.0);
    
    // Shadow mapping
    float shadow = 0.0;
    vec4 fragPosLightSpace = lightSpaceMatrix * worldPosition;
    vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
    projCoords = projCoords * 0.5 + 0.5;
    
    if (projCoords.z <= 1.0) {
        float currentDepth = projCoords.z;
        float bias = max(0.01 * (1.0 - dot(normal, dirLightDirNorm)), 0.001);
        
        vec2 shadowUV = projCoords.xy;
        // Since we already flipped the projection matrix Y in Lua,
        // we might not need to flip UV here, but let's check.
        // Actually, NDC to UV is always (x*0.5+0.5, y*0.5+0.5).
        // If projection was flipped, the NDC Y is already corrected for texture space.

        // PCF (Percentage-Closer Filtering)
        vec2 texelSize = 1.0 / vec2(textureSize(shadowMap, 0));
        for(int x = -1; x <= 1; ++x) {
            for(int y = -1; y <= 1; ++y) {
                float pcfDepth = texture(shadowMap, shadowUV + vec2(x, y) * texelSize).r; 
                shadow += (currentDepth - bias > pcfDepth) ? 1.0 : 0.0;        
            }    
        }
        shadow /= 9.0;
    }
    
    // Directional Specular
    vec3 dirReflectDir = reflect(-dirLightDirNorm, normal);
    float dirSpec = pow(max(dot(viewDir, dirReflectDir), 0.0), shininess);
    
    // Add a small amount of "wrap" lighting for a softer look on characters
    float wrap = 0.2;
    float dirDiffWrap = max(0.0, (dot(normal, dirLightDirNorm) + wrap) / (1.0 + wrap));
    lighting += dirLightColor * (dirDiffWrap + dirSpec * specIntensity) * (1.0 - shadow);
    
    for (int i = 0; i < MAX_LIGHTS; i++) {
        if (i >= numLights) break;
        
        vec3 lightDir = lightPositions[i] - worldPosition.xyz;
        float dist = length(lightDir);
        
        // Optimization: skip if out of range
        if (dist > lightIntensities[i]) continue;

        lightDir = normalize(lightDir);
        
        // Diffuse
        float diff = max(dot(normal, lightDir), 0.0);
        
        // Specular
        vec3 reflectDir = reflect(-lightDir, normal);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
        
        // Attenuation (Linear falloff)
        float attenuation = max(0.0, 1.0 - dist / lightIntensities[i]);

        lighting += lightColors[i] * (diff + spec * specIntensity) * attenuation;
    }

    if (unlit) {
        return vec4(albedo * vertexColor.rgb * color.rgb, texColor.a * vertexColor.a);
    }

    vec3 finalColor = albedo * vertexColor.rgb * color.rgb * lighting;

    // Emissive materials (matIndex >= 240)
    if (matIndex >= 240) {
        // Ghost voxels (matIndex >= 250)
        if (matIndex >= 250) {
            // Massive boost to trigger bloom even with low alpha
            finalColor += albedo * vertexColor.rgb * color.rgb * 100.0;
            return vec4(finalColor, 0.01);
        }
        
        // Normal emissive: boost albedo to trigger bloom
        // We use a high multiplier to ensure it stays bright even with fog
        finalColor += albedo * vertexColor.rgb * color.rgb * 3.0;
    }


    
    // Distance Fog
    float dist = length(viewPosition.xyz);
    float fogFactor = clamp((dist - fogNear) / (fogFar - fogNear), 0.0, 1.0);
    finalColor = mix(finalColor, fogColor, fogFactor);

    return vec4(finalColor, texColor.a * vertexColor.a);
}
#endif
