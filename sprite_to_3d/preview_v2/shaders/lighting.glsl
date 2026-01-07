#pragma language glsl3

#ifdef VERTEX
attribute vec3 VertexNormal;

uniform mat4 m_projection;
uniform mat4 m_view;
uniform mat4 m_model;

varying vec4 v_worldPos;
varying vec3 v_normal;
varying vec4 v_color;
varying vec2 v_texCoord;

vec4 position(mat4 transformProjection, vec4 vertexPosition) {
    v_worldPos = m_model * vertexPosition;
    v_normal = normalize(mat3(m_model) * VertexNormal);
    v_color = VertexColor;
    v_texCoord = VertexTexCoord.xy;
    
    return m_projection * m_view * v_worldPos;
}
#endif

#ifdef PIXEL
varying vec4 v_worldPos;
varying vec3 v_normal;
varying vec4 v_color;
varying vec2 v_texCoord;

uniform vec3 ambientColor;
uniform float ambientIntensity;
uniform vec3 dirLightDirection;
uniform vec3 dirLightColor;
uniform vec3 eyePosition;
uniform vec4 baseColor;
uniform bool unlit;

vec4 effect(vec4 color, Image tex, vec2 texture_coords, vec2 screen_coords) {
    // Use v_texCoord from vertex shader
    vec4 texColor = Texel(tex, v_texCoord);
    if (texColor.a < 0.1) discard;

    vec4 tint = v_color * baseColor * color;

    if (unlit) {
        return vec4(texColor.rgb * tint.rgb, texColor.a * tint.a);
    }

    vec3 normal = normalize(v_normal);
    vec3 lightDir = normalize(-dirLightDirection);
    float diff = max(0.2, dot(normal, lightDir));
    
    vec3 lighting = (ambientColor * ambientIntensity) + (dirLightColor * diff);

    return vec4(texColor.rgb * tint.rgb * lighting, texColor.a * tint.a);
}
#endif