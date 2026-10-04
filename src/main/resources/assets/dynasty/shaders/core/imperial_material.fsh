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
    // These are world-space apparitions, not camera overlays. Cull only fragments
    // intersecting the viewer, before they can write depth. Keep the full mesh,
    // silhouette and scale for every observer (including another player's camera).
    // Use signed camera DEPTH, not radial distance: the corners of a large
    // cape can be far radially while its plane still cuts across the near plane.
    float cameraDepth = max(0.0, -viewPosition.z);
    color.a *= smoothstep(0.65, 2.50, cameraDepth);
    // Closed armor's inward-facing surfaces must not enclose a flying camera.
    // Keep intentionally two-sided ribbons/cloth at ordinary viewing distances.
    if (cameraDepth < 3.0 && dot(surfaceNormal, -viewPosition) < 0.0) discard;
    if (color.a <= threshold(ivec2(gl_FragCoord.xy))) discard;
    bool cloth = MaterialMode > 0.5 && (distance(vertexColor.rgb, RobeColorA) < 0.008
                                     || distance(vertexColor.rgb, RobeColorB) < 0.008);
    vec3 woven = vec3(0.0);
    // Dedicated appended palette entries: no changes to armor, face, beard or cape shading.
    bool blade = MaterialMode > 0.5 && distance(vertexColor.rgb, vec3(.045,.155,.145)) < .005;
    bool bevel = MaterialMode > 0.5 && distance(vertexColor.rgb, vec3(.49,.65,.70)) < .005;
    bool cutting = MaterialMode > 0.5 && distance(vertexColor.rgb, vec3(.79,.87,.91)) < .005;
    bool relief = MaterialMode > 0.5 && distance(vertexColor.rgb, vec3(.22,.36,.29)) < .005;
    bool socket = MaterialMode > 0.5 && distance(vertexColor.rgb, vec3(.46,.32,.13)) < .005;
    bool shaft = MaterialMode > 0.5 && distance(vertexColor.rgb, vec3(.055,.070,.058)) < .005;
    bool weaponMetal = blade || bevel || cutting || relief || socket;
    float forge = 0.0;
    if (weaponMetal || shaft) {
        vec3 cell = floor(modelPosition * vec3(85.0, 95.0, 65.0));
        float grain = fract(sin(dot(cell, vec3(12.9898,78.233,37.719))) * 43758.5453);
        float detailFade = 1.0-smoothstep(.20,.85,length(fwidth(modelPosition))*95.0);
        forge = (grain-.5)*detailFade;
        float scratchCoordinate = dot(modelPosition.xy, vec2(130.0,11.0));
        float scratch = pow(max(0.0,sin(scratchCoordinate)),40.0)
                      * step(.91,grain)*detailFade;
        color.rgb *= 1.0 + (shaft ? .11 : .055)*forge + .055*scratch;
        if (shaft) color.rgb *= .96+.04*sin(modelPosition.y*5.0+sin(modelPosition.x*160.0)*2.0);
    }
    bool vermilion = MaterialMode > 0.5 && distance(vertexColor.rgb, vec3(0.66, 0.075, 0.075)) < 0.008;
    if (vermilion) {
        // Model-space pigment cells stay fixed while the guardian/camera moves. No random shimmer.
        vec3 cell = floor(modelPosition * 24.0);
        float pigment = fract(sin(dot(cell, vec3(12.9898, 78.233, 37.719))) * 43758.5453);
        float temple = smoothstep(0.20, 0.46, abs(modelPosition.x));
        color.rgb *= 0.91 + floor(pigment * 3.0) * 0.025 - temple * 0.035;
        if (modelPosition.y > 7.4 && modelPosition.y < 8.3 && modelPosition.z > 0.15) {
            vec2 face = floor(modelPosition.xy * 24.0) / 24.0;
            float socket = exp(-pow((abs(face.x)-0.23)/0.12,2.0)-pow((face.y-7.94)/0.08,2.0));
            float ridge = exp(-pow(face.x/0.085,2.0)-pow((face.y-7.82)/0.22,2.0));
            float cheek = exp(-pow((abs(face.x)-0.30)/0.12,2.0)-pow((face.y-7.72)/0.12,2.0));
            color.rgb *= 1.0 - 0.055 * socket + 0.025 * ridge + 0.018 * cheek;
        }
    }
    if (cloth) {
        woven = brocade(modelPosition, modelNormal);
        // Blend in linear light; reflected gold thread never changes face, beard or metal materials.
        color.rgb = pow(mix(pow(color.rgb, vec3(2.2)), pow(woven, vec3(2.2)), 0.6), vec3(1.0 / 2.2));
    }
    vec3 n = surfaceNormal / max(length(surfaceNormal), 0.00001);
    vec3 v = -viewPosition / max(length(viewPosition), 0.00001);
    // Open cloth, whisker ribbons and mirrored geometry are intentionally two-sided.
    if (dot(n, v) < 0.0) n = -n;
    vec3 key = normalize(keyDirection);
    vec3 fill = normalize(fillDirection);
    float warmMetal = smoothstep(0.09, 0.27, color.r - color.b) * smoothstep(0.23, 0.55, color.g);
    float paleMetal = smoothstep(0.66, 0.86, min(color.r, min(color.g, color.b)));
    float metal = max(warmMetal, paleMetal * 0.55);
    if (weaponMetal) metal = cutting ? .95 : bevel ? .88 : .72;
    if (shaft) metal = 0.0;
    if (cloth) metal = 0.0;
    float diffuse = 0.32 + 0.64 * max(0.0, dot(n, key)) + 0.19 * max(0.0, dot(n, fill));
    float roughnessVariation = cloth ? mix(0.92, 1.08, dot(woven, vec3(0.2126, 0.7152, 0.0722))) : weaponMetal ? 1.0+forge*.16 : 1.0;
    float highlight = pow(max(0.0, dot(n, normalize(key + v))), mix(26.0, 80.0, metal) * roughnessVariation);
    float rim = pow(1.0 - max(0.0, dot(n, v)), 3.0);
    vec3 light = color.rgb * diffuse * (0.48 + 0.52 * SceneLight);
    vec3 specularTint = (blade || bevel || cutting || relief) ? vec3(.66,.85,.94)
                       : mix(vec3(0.8, 0.88, 1.0), vec3(1.0, 0.87, 0.64), metal);
    light += specularTint * highlight * (vermilion ? 0.012 : shaft ? .018 : mix(0.055, 0.42, metal)) * SceneLight;
    // Rim separates silhouettes; it must not wash out dark beard and face details.
    light += color.rgb * vec3(0.13, 0.17, 0.20) * rim;
    // Dedicated dragon eye glint material only; scales and pale armor stay normally shaded.
    if (distance(color.rgb, vec3(212.0 / 255.0, 1.0, 1.0)) < 0.008) {
        light = max(light, color.rgb);
    }
    float fog = smoothstep(FogStart, max(FogStart + 0.001, FogEnd), length(viewPosition));
    fragColor = vec4(mix(clamp(light, 0.0, 1.0), FogColor.rgb, fog * FogColor.a), 1.0);
}
