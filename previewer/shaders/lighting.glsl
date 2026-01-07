#pragma language glsl3

#ifdef VERTEX
// LÖVE 11 built-in attributes:
// attribute vec4 VertexPosition;
// attribute vec4 VertexColor;
// attribute vec2 VertexTexCoord;

attribute vec3 VertexNormal;

uniform mat4 m_projection;
uniform mat4 m_view;
uniform mat4 m_model;

varying vec4 worldPosition;
varying vec4 viewPosition;
varying vec3 vertexNormal;
varying vec4 vertexColor;
varying vec2 texCoord;

vec4 position(mat4 transform_projection, vec4 vertex_position) {
    worldPosition = m_model * vertex_position;
    viewPosition = m_view * worldPosition;
    
    vertexNormal = normalize(mat3(m_model) * VertexNormal);
    vertexColor = VertexColor;
    // Explicit cast to vec2 to avoid conversion errors
    texCoord = texture_coords; // LÖVE 11 provides 'texture_coords' to position() too? No.
    // Wait, LÖVE 11's VertexTexCoord is available.
    texCoord = VertexTexCoord; 

    return m_projection * viewPosition;
}
#endif

#ifdef PIXEL
varying vec4 worldPosition;
varying vec4 viewPosition;
varying vec3 vertexNormal;
varying vec4 vertexColor;
varying vec2 texCoord;

uniform vec3 ambientColor;
uniform float ambientIntensity;
uniform vec3 dirLightDirection;
uniform vec3 dirLightColor;
uniform bool unlit;

vec4 effect(vec4 color, Image tex, vec2 texture_coords, vec2 screen_coords) {
    // Use the varying texCoord we passed from vertex shader
    vec4 texColor = Texel(tex, texCoord);
    if (texColor.a < 0.1) discard;

    if (unlit) {
        return vec4(texColor.rgb * vertexColor.rgb * color.rgb, texColor.a * vertexColor.a);
    }

    vec3 normal = normalize(vertexNormal);
    vec3 lighting = ambientColor * ambientIntensity;
    
    vec3 dirLightDirNorm = normalize(-dirLightDirection);
    float diff = max(dot(normal, dirLightDirNorm), 0.0);
    lighting += dirLightColor * diff;

    return vec4(texColor.rgb * vertexColor.rgb * color.rgb * lighting, texColor.a * vertexColor.a);
}
#endif
