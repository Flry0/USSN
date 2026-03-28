Shader "Custom/SpaceSun"
{
    Properties
    {
        [Header(Core Setup)]
        _MainTex ("Base Texture", 2D) = "white" {}
        [HDR] _MainColor ("Core Dark Color", Color) = (1, 0.2, 0, 1)
        [HDR] _EmissionColor ("Core Bright Color", Color) = (1, 0.8, 0, 1)
        _EmissionIntensity ("Core Glow Intensity", Float) = 3.0
        _NoiseScale ("Core Noise Scale", Float) = 5.0
        _Speed ("Plasma Speed", Float) = 0.5
        
        [Header(Light Rays and Corona Setup)]
        [HDR] _RayColor ("Ray Color", Color) = (1, 0.6, 0.1, 1)
        _RayLength ("Ray Length Scale", Float) = 1.6
        _RayDensity ("Ray Noise Density", Float) = 8.0
        _RaySpeed ("Ray Move Speed", Float) = 1.0
        _RayPower ("Ray Sharpness", Float) = 4.0
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" }
        LOD 100

        // Opaque Surface
        Pass
        {
            ZWrite On
            Cull Back
            Blend One Zero
            
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float4 vertex : SV_POSITION;
                float3 localPos : TEXCOORD0;
                float3 normal : TEXCOORD1;
                float2 uv : TEXCOORD2;
            };

            sampler2D _MainTex;
            float4 _MainTex_ST;
            float4 _MainColor;
            float4 _EmissionColor;
            float _EmissionIntensity;
            float _NoiseScale;
            float _Speed;

            float hash(float3 p) {
                p = frac(p * 0.3183099 + .1);
                p *= 17.0;
                return frac(p.x * p.y * p.z * (p.x + p.y + p.z));
            }

            float noise(float3 x) {
                float3 p = floor(x);
                float3 f = frac(x);
                f = f * f * (3.0 - 2.0 * f);
                return lerp(
                    lerp(lerp(hash(p + float3(0,0,0)), hash(p + float3(1,0,0)), f.x),
                         lerp(hash(p + float3(0,1,0)), hash(p + float3(1,1,0)), f.x), f.y),
                    lerp(lerp(hash(p + float3(0,0,1)), hash(p + float3(1,0,1)), f.x),
                         lerp(hash(p + float3(0,1,1)), hash(p + float3(1,1,1)), f.x), f.y), f.z);
            }

            float fbm(float3 p) {
                float f = 0.0;
                f += 0.5 * noise(p); p *= 2.02;
                f += 0.25 * noise(p); p *= 2.03;
                f += 0.125 * noise(p); p *= 2.01;
                f += 0.0625 * noise(p);
                return f / 0.9375;
            }

            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.localPos = v.vertex.xyz;
                o.normal = UnityObjectToWorldNormal(v.normal);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                float t = _Time.y * _Speed;
                float3 noisePos = i.localPos * _NoiseScale;
                
                float n1 = fbm(noisePos + float3(t, t, t));
                float n2 = fbm(noisePos - float3(t, t*0.5, t*0.8) + float3(100, 100, 100));
                float plasma = (n1 + n2) * 0.5;
                plasma = smoothstep(0.3, 0.7, plasma);

                fixed4 texColor = tex2D(_MainTex, i.uv);
                float3 albedo = lerp(_MainColor.rgb * texColor.rgb, _EmissionColor.rgb, plasma);
                return fixed4(albedo * _EmissionIntensity, 1.0);
            }
            ENDCG
        }

        // Additive Corona
        Pass
        {
            ZWrite Off
            Cull Off
            Blend One One
            
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
            };

            struct v2f
            {
                float4 vertex : SV_POSITION;
                float3 localPos : TEXCOORD0;
                float3 viewDir : TEXCOORD1;
            };

            float4 _RayColor;
            float _RayLength;
            float _RayDensity;
            float _RaySpeed;
            float _RayPower;

            float hash(float3 p) {
                p = frac(p * 0.3183099 + .1);
                p *= 17.0;
                return frac(p.x * p.y * p.z * (p.x + p.y + p.z));
            }

            float noise(float3 x) {
                float3 p = floor(x);
                float3 f = frac(x);
                f = f * f * (3.0 - 2.0 * f);
                return lerp(
                    lerp(lerp(hash(p + float3(0,0,0)), hash(p + float3(1,0,0)), f.x),
                         lerp(hash(p + float3(0,1,0)), hash(p + float3(1,1,0)), f.x), f.y),
                    lerp(lerp(hash(p + float3(0,0,1)), hash(p + float3(1,0,1)), f.x),
                         lerp(hash(p + float3(0,1,1)), hash(p + float3(1,1,1)), f.x), f.y), f.z);
            }

            float fbm(float3 p) {
                float f = 0.0;
                f += 0.5 * noise(p); p *= 2.02;
                f += 0.25 * noise(p); p *= 2.03;
                f += 0.125 * noise(p); p *= 2.01;
                f += 0.0625 * noise(p);
                return f / 0.9375;
            }

            v2f vert (appdata v)
            {
                v2f o;
                
                // Arka yüzeyleri (kürenin içini değil arkasını) çizdiğimiz için verteksleri dışarı doğru büyütüyoruz.
                // Bu sayede modelin orijinal sınırlarının dışına çıkıp bir "halo" veya ışın kabuğu oluşturuyoruz.
                // Arka yüzeyleri çizdiğimiz için verteksleri dışarı doğru (normal yönlerinde) büyütüyoruz.
                // Modeli merkezden dışarı doğru ölçeklendiriyoruz ki baz mesh'in boyutu ne olursa olsun oransal büyüsün
                float3 expandedVertex = v.vertex.xyz * _RayLength; 
                o.vertex = UnityObjectToClipPos(expandedVertex);
                
                // Gürültünün sürekli ve düzgün olması için objenin normal vektörlerini baz alıyoruz
                o.localPos = v.normal;
                
                float3 worldPos = mul(unity_ObjectToWorld, float4(expandedVertex, 1.0)).xyz;
                o.viewDir = normalize(UnityWorldSpaceViewDir(worldPos));
                
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                float t = _Time.y * _RaySpeed;
                
                // Dinamik güneş patlaması / ışın hüzmesi şekli oluştur
                float noiseVal = fbm(i.localPos * _RayDensity - float3(t, t*0.5, 0));
                
                // Işınların keskinliğini artır (Power)
                float rayShape = pow(abs(noiseVal), _RayPower);

                // Artık kenarlarda kaybolmasını (shellFade) siliyoruz, Cull Off sayesinde rays daha gür ve belirgin görünecek
                float finalIntensity = rayShape * 5.0;

                return fixed4(_RayColor.rgb * finalIntensity, 1.0);
            }
            ENDCG
        }
    }
}
