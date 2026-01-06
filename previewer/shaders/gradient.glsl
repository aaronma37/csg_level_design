extern vec3 topColor;
extern vec3 bottomColor;

vec4 effect(vec4 color, Image texture, vec2 texture_coords, vec2 screen_coords) {
    float t = screen_coords.y / love_ScreenSize.y;
    vec3 result = mix(topColor, bottomColor, t);
    return vec4(result, 1.0);
}
