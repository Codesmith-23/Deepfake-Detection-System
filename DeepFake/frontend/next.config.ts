// module.exports = {
//   images: {
//     remotePatterns: [
//       {
//         protocol: 'http',
//         hostname: 'localhost',
//         port: '5000',
//         pathname: '/uploads/flagged_frames/**',
//       },
//     ],
//   },
// };

/** @type {import('next').NextConfig} */
module.exports = {
  eslint: {
  ignoreDuringBuilds: true,},
  devIndicators: false, // This removes the Turbopack/lightning bolt icon
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '5000',
        pathname: '/uploads/flagged_frames/**',
      },
    ],
  },
};