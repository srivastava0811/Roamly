/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: [
    '@roamly/api-client',
    '@roamly/design-tokens',
    '@roamly/shared-types',
    '@roamly/shared-utils',
  ],
};

export default nextConfig;
