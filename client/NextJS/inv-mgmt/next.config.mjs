/** @type {import('next').NextConfig} */

const API_URL = process.env.API_URL

/*
nextConfig = {
	async rewrites() {
        console.log("*** rewrites " + API_URL);
		return [
			{
				source: '/service/:path',
				// destination: `${API_URL}/:path*`,
                destination: `http://localhost:8000/invmgmt/:path`,
			},
            {
				source: '/amazon',
				// destination: `${API_URL}/:path*`,
                destination: `http://www.yahoo.com`,
			},
		]
	},
};

export default nextConfig;
*/

const nextConfig = {
    // trailingSlash: true,
    async rewrites() {
      return [
        {
          source: '/api/:path',
          destination: 'http://localhost/service/invmgmt/:path',
        },
      ]
    },
  }
export default nextConfig;