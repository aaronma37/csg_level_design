#pragma language glsl3

uniform float threshold = 1.0;

vec4 effect(vec4 color, Image tex, vec2 texCoord, vec2 screen_coords) {
    vec4 texColor = Texel(tex, texCoord);
    // Simple brightness extraction (luminance)
    float brightness = dot(texColor.rgb, vec3(0.2126, 0.7152, 0.0722));
    if (brightness > threshold) {
        return texColor;
    }
    return vec4(0.0, 0.0, 0.0, 1.0);
}
