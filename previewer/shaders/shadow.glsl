#pragma language glsl3

#ifdef VERTEX
uniform mat4 m_projection;
uniform mat4 m_view;
uniform mat4 m_model;

vec4 position(mat4 transformProjection, vec4 vertexPosition) {
    return m_projection * m_view * m_model * vertexPosition;
}
#endif

#ifdef PIXEL
vec4 effect(vec4 color, Image tex, vec2 texture_coords, vec2 screen_coords) {
    if (Texel(tex, texture_coords).a < 0.1) discard;
    return vec4(vec3(gl_FragCoord.z), 1.0);
}
#endif
