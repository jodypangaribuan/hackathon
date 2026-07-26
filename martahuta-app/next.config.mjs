/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Standalone output = image Docker ramping untuk deployment DGX B200.
  output: "standalone",
};

export default nextConfig;
