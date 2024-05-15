import mongoose from 'mongoose';
// mongoose.set('strictQuery', true);
const UsersSchema = new mongoose.Schema(
	{
		fullname: { type: String, required: true },
		username: {type: String, required: true},
		email: { type: String, required: true },
		passion: { type: String, required: false },
		avatar: { type: String, required: false },
		password: { type: String, required: true }
	},
	{ timestamps: true }
);
export const Users: any = mongoose.models.users || mongoose.model('users', UsersSchema);
