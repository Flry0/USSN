Shader "USSN/SolarWave"
{
    Properties
    {
        [HDR] _CoreColor ("Start Color (Sun)", Color) = (1, 0.6, 0.1, 1)
        [HDR] _OuterColor ("End Color (Electro)", Color) = (0, 0.8, 1, 1)
        _TransitionDist ("Color Transition Distance", Float) = 150.0
        _Speed ("Wave Speed", Float) = 2.0
        _FresnelPower ("Fresnel Sharpness", Float) = 3.0
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" }
        LOD 200

        CGPROGRAM
        // Surface shader for absolute compatibility
        #pragma surface surf Standard alpha:fade
        #pragma target 3.0

        struct Input
        {
            float3 worldPos;
            float3 viewDir;
            float3 worldNormal;
        };

        float4 _CoreColor;
        float4 _OuterColor;
        float _TransitionDist;
        float _Speed;
        float _FresnelPower;

        void surf (Input IN, inout SurfaceOutputStandard o)
        {
            // Fresnel effect
            float fresnel = pow(1.0 - saturate(abs(dot(normalize(IN.viewDir), normalize(IN.worldNormal)))), _FresnelPower);
            
            // Pulsing effect
            float pulse = 0.5 + 0.5 * sin(_Time.y * _Speed + IN.worldPos.x * 0.1);
            float intensity = fresnel * (0.5 + 0.5 * pulse);

            // Color transition based on distance
            float dist = length(IN.worldPos);
            float blend = saturate(dist / _TransitionDist);
            float3 finalColor = lerp(_CoreColor.rgb, _OuterColor.rgb, blend);

            // Output
            o.Albedo = 0; // Pure emission
            o.Emission = finalColor * intensity * 5.0;
            o.Alpha = intensity * 0.8;
        }
        ENDCG
    }
    FallBack "Transparent/Diffuse"
}
