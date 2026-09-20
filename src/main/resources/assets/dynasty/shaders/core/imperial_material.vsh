#version 150

in vec3 Position;
in vec4 Color;
in vec3 Normal;

uniform mat4 ModelViewMat;
uniform mat4 WorldViewMat;
uniform mat4 LightViewMat;
uniform mat4 LocalFromPosition;
uniform mat4 ProjMat;

out vec4 vertexColor;
out vec3 viewPosition;
out vec3 surfaceNormal;
out vec3 keyDirection;
out vec3 fillDirection;
out vec3 modelPosition;
out vec3 modelNormal;

void main() {
    vec4 view = ModelViewMat * vec4(Position, 1.0);
    gl_Position = ProjMat * view;
    viewPosition = view.xyz;
    mat3 orientation = mat3(ModelViewMat) * mat3(WorldViewMat);
    surfaceNormal = orientation * Normal;
    mat3 lightOrientation = mat3(ModelViewMat) * mat3(LightViewMat);
    keyDirection = lightOrientation * normalize(vec3(-0.45, 0.8, 0.6));
    fillDirection = lightOrientation * normalize(vec3(0.7, 0.35, -0.45));
    modelPosition = (LocalFromPosition * vec4(Position, 1.0)).xyz;
    modelNormal = mat3(LocalFromPosition) * mat3(WorldViewMat) * Normal;
    vertexColor = Color;
}
