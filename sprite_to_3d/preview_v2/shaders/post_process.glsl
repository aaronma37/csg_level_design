#pragma language glsl3

uniform sampler2D sceneTex;
uniform sampler2D blurTex;
uniform sampler2D depthTex;
uniform sampler2D bloomTex;

uniform float focusDepth;
uniform float focusRange;
uniform float blurFar;
uniform float blurNear;
uniform float bloomIntensity;

vec4 effect(vec4 color, Image tex, vec2 texCoord, vec2 screen_coords) {
    vec4 sceneColor = Texel(sceneTex, texCoord);
    vec4 blurColor = Texel(blurTex, texCoord);
    float depth = Texel(depthTex, texCoord).r;

    // Calculate blur factor based on distance from focusDepth
    float dist = abs(depth - focusDepth);
    float factor = smoothstep(focusRange, focusRange + blurFar, dist);
    
    if (depth < focusDepth) {
        factor = smoothstep(focusRange, focusRange + blurNear, dist);
    }

    vec4 finalColor = mix(sceneColor, blurColor, factor);
    
    // Add Bloom
    vec3 bloomColor = Texel(bloomTex, texCoord).rgb;
    finalColor.rgb += bloomColor * bloomIntensity;

    return finalColor;
}
