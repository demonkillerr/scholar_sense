import type { NextConfig } from 'next';
import path from 'path';

const nextConfig: NextConfig = {
  // async rewrites() {
  //   return [
  //     {
  //       source: '/uploads/:path*', // Match any request starting with /uploads
  //       destination: path.join(__dirname, '..', 'uploads', ':path*'), // Serve files from the uploads folder
  //     },
  //   ];
  // },
};

export default nextConfig;