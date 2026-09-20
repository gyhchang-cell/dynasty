#version 150

uniform vec4 ColorModulator;
uniform float SceneLight;
uniform float FogStart;
uniform float FogEnd;
uniform vec4 FogColor;
uniform sampler2D Sampler0;
uniform float MaterialMode;
uniform float MeshOpacity;
uniform vec3 RobeColorA;
uniform vec3 RobeColorB;

in vec4 vertexColor;
in vec3 viewPosition;
in vec3 surfaceNormal;
in vec3 keyDirection;
in vec3 fillDirection;
in vec3 modelPosition;
in vec3 modelNormal;
out vec4 fragColor;

// Stable screen-door reveal: surviving fragments write depth, so internal faces never bleed through.
float threshold(ivec2 pixel) {
    int x = pixel.x & 3;
    int y = pixel.y & 3;
    int a = ((x & 1) << 1) | ((x & 1) ^ (y & 1));
    int b = (((x >> 1) & 1) << 1) | (((x >> 1) & 1) ^ ((y >> 1) & 1));
    return (float(4 * a + b) + 0.5) / 16.0;
}

vec2 mirrorTile(vec2 uv) {
    return 1.0 - abs(mod(uv, 2.0) - 1.0);
}

vec3 brocade(vec3 p, vec3 normal) {
    vec3 weight = pow(abs(normalize(normal)), vec3(4.0));
    weight /= max(0.0001, weight.x + weight.y + weight.z);
    vec3 x = texture(Sampler0, mirrorTile(p.zy * 0.6)).rgb;
    vec3 y = texture(Sampler0, mirrorTile(p.xz * 0.6)).rgb;
    vec3 z = texture(Sampler0, mirrorTile(p.xy * 0.6)).rgb;
    return x * weight.x + y * weight.y + z * weight.z;
}

void main() {
    vec4 color = vertexColor * ColorModulator;
    color.a *= MeshOpacity;
    if (color.a <= threshold(ivec2(gl_FragCoord.xy))) discard;
    bool cloth = MaterialMode > 0.5 && (distance(vertexColor.rgb, RobeColorA) < 0.008
                                     || distance(vertexColor.rgb, RobeColorB) < 0.008);
    vec3 woven = vec3(0.0);
    if (cloth) {
        woven = brocade(modelPosition, modelNormal);
        // Blend in linear light; reflected gold thread never changes face, beard or metal materials.
        color.rgb = pow(mix(pow(color.rgb, vec3(2.2)), pow(woven, vec3(2.2)), 0.6), vec3(1.0 / 2.2));
    }
    vec3 n = normalize(surfaceNormal);
    vec3 v = normalize(-viewPosition);
    // Open cloth, whisker ribbons and mirrored geometry are intentionally two-sided.
    if (dot(n, v) < 0.0) n = -n;
    vec3 key = normalize(keyDirection);
    vec3 fill = normalize(fillDirection);
    float warmMetal = smoothstep(0.09, 0.27, color.r - color.b) * smoothstep(0.23, 0.55, color.g);
    float paleMetal = smoothstep(0.66, 0.86, min(color.r, min(color.g, color.b)));
    float metal = max(warmMetal, paleMetal * 0.55);
    if (cloth) metal = 0.0;
    float diffuse = 0.32 + 0.64 * max(0.0, dot(n, key)) + 0.19 * max(0.0, dot(n, fill));
    float roughnessVariation = cloth ? mix(0.92, 1.08, dot(woven, vec3(0.2126, 0.7152, 0.0722))) : 1.0;
    float highlight = pow(max(0.0, dot(n, normalize(key + v))), mix(26.0, 80.0, metal) * roughnessVariation);
    float rim = pow(1.0 - max(0.0, dot(n, v)), 3.0);
    vec3 light = color.rgb * diffuse * (0.48 + 0.52 * SceneLight);
    light += mix(vec3(0.8, 0.88, 1.0), vec3(1.0, 0.87, 0.64), metal)
           * highlight * mix(0.055, 0.42, metal) * SceneLight;
    // Rim separates silhouettes; it must not wash out dark beard and face details.
    light += color.rgb * vec3(0.13, 0.17, 0.20) * rim;
    // Dedicated dragon eye glint material only; scales and pale armor stay normally shaded.
    if (distance(color.rgb, vec3(212.0 / 255.0, 1.0, 1.0)) < 0.008) {
        light = max(light, color.rgb);
    }
    float fog = smoothstep(FogStart, max(FogStart + 0.001, FogEnd), length(viewPosition));
    fragColor = vec4(mix(clamp(light, 0.0, 1.0), FogColor.rgb, fog * FogColor.a), 1.0);
}
