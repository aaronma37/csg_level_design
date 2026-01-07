#pragma language glsl3

vec4 effect(vec4 color, Image tex, vec2 texCoord, vec2 screen_coords) {
    vec2 texelSize = 1.0 / vec2(love_ScreenSize.xy);
    float result = 0.0;
    for (int x = -2; x < 2; ++x) {
        for (int y = -2; y < 2; ++y) {
            vec2 offset = vec2(float(x), float(y)) * texelSize;
            result += Texel(tex, texCoord + offset).r;
        }
    }
    return vec4(vec3(result / 16.0), 1.0);
}
