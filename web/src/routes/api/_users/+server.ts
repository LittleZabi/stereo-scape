// @ts-ignore
import database from '$lib/database_ops/database';
// @ts-ignore
import { Users } from '$lib/database_ops/models';
import { signUp } from './users_ops';

await database.connect();
export const POST = async ({ request }: any) => {
	const req = request.headers.get('request');
	if (req === 'sign_up') {
        return signUp(await request.formData())
	}
	return new Response(
		JSON.stringify({ message: "Don't try to access api without authorization!" }),
		{ status: 401 }
	);
};
export const GET = async ({ url }: any) => {
	if (url.searchParams.get('username')) {
		const u = url.searchParams.get('username');
		const user = await Users.countDocuments({ username: u });
		return new Response(JSON.stringify({ user }), { status: 200 });
	}
	return new Response(JSON.stringify({ message: 'API working fine' }));
};
