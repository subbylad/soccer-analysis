import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Remove experimental turbo config for Vercel compatibility
  images: {
    domains: ['localhost'],
  },
  webpack: (config) => {
    config.module.rules.push({
      test: /\.svg$/i,
      issuer: /\.[jt]sx?$/,
      use: ['@svgr/webpack'],
    });
    return config;
  },
  // Remove output for Vercel compatibility
  // output: 'standalone',
};

export default nextConfig;
