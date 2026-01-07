#define KERNEL_SIZE 9 // Number of samples
uniform vec2 u_direction; // (1.0, 0.0) for horizontal, (0.0, 1.0) for vertical
uniform vec2 u_screenSize;

// Pre-calculated Gaussian weights (adjust as needed for desired blur strength)
const float weights[KERNEL_SIZE] = float[](
    0.0262162162, 0.0340540541, 0.1216216216, 0.1945945946, 0.2270270270,
    0.1945945946, 0.1216216216, 0.0340540541, 0.0262162162
);

vec4 effect(vec4 color, Image texture, vec2 texture_coords, vec2 pixel_coords) {
    vec4 sum = vec4(0.0);
    int center = KERNEL_SIZE / 2; 
    vec2 texelSize = 1.0 / u_screenSize;
    for (int i = 0; i < KERNEL_SIZE; i++)
    {
        float offset = float(i - center);
        vec2 newTexCoords = texture_coords + u_direction * offset * texelSize;
        vec4 sample = Texel(texture, newTexCoords);
        sum += sample * weights[i];
    }
    return sum;
}
