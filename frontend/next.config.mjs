const basePath = process.env.NODE_ENV === "production" ? "/job-board" : "";

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  basePath,
  trailingSlash: true,
  images: { unoptimized: true },
};
export default nextConfig;
