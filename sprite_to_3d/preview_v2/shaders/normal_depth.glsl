#pragma language glsl3

#ifdef VERTEX
uniform mat4 m_projection;
uniform mat4 m_view;
uniform mat4 m_model;

attribute vec3 VertexNormal;

varying vec3 vNormal;
varying float vDepth;
varying vec2 vTexCoord;

vec4 position(mat4 transformProjection, vec4 vertexPosition) {
    vec4 worldPosition = m_model * vertexPosition;
    vec4 viewPosition = m_view * worldPosition;
    
    vNormal = normalize(mat3(m_view * m_model) * VertexNormal); // Normal in view space
    vDepth = -viewPosition.z; // Depth in view space (positive)
    vTexCoord = VertexTexCoord.xy;

    return m_projection * viewPosition;
}
#endif

#ifdef PIXEL
varying vec3 vNormal;
varying float vDepth;
varying vec2 vTexCoord;

uniform sampler2D MainTex;

void effect() {
    if (Texel(MainTex, vTexCoord).a < 0.5) discard;
    
    // Output view-space normal to first canvas
    love_Canvases[0] = vec4(vNormal * 0.5 + 0.5, 1.0);
    // Output view-space depth to second canvas
    love_Canvases[1] = vec4(vDepth, vDepth, vDepth, 1.0);
}
#endif
