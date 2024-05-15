<script lang="ts">
	import { WEBSITE_NAME } from '../lib/config';
	import axios from 'axios';
	import Icon from '@iconify/svelte';
	import { Cookies, createForm } from '../lib/globals';
	let interval = undefined;
	let message: any | { message: string; variant: string } = false
	const filterUsername: (text: string) => string = (text) => text.replace(/[^a-zA-Z_]/g, '');
	const dataset = {
		fullname: '',
		username: '',
		email: '',
		passion: '',
		password: '',
		rePassword: '',
		avatar: undefined
	};
	const showMessage = (
		id: string,
		body: { text: string; variant: string; cssClass?: string },
		focus = true
	) => {
		const target = document.getElementById(id);
		if (focus) target.focus();
		const isExist = target.parentElement.querySelector(`.message`);
		if (isExist) {
			isExist.innerHTML = body.text;
			isExist.classList.remove('alert');
			isExist.classList.remove('success');
			isExist.classList.remove('danger');
			isExist.classList.add(body.variant);
			return 0;
		}
		target.style.borderBottomColor = 'orangered';
		const new_ = document.createElement('span');
		new_.innerText = body.text;
		new_.classList.add('message');
		new_.classList.add('inline');
		new_.classList.add(body.variant);
		if (body.cssClass) new_.classList.add(body.cssClass);
		target.parentElement.appendChild(new_);
	};
	const removeMessage: (input_id: string | Array<Array<string>>, span_id?: string) => void = (
		input_id,
		span_id
	) => {
		const rem = (id: string, span: string) => {
			try {
				const p: HTMLElement = document.querySelector(id);
				p.style.borderBottomColor = '#ffffff21';
				let k = p.parentElement.querySelector(span);
				k.remove();
			} catch (e) {}
		};
		if (typeof input_id === 'string') rem(input_id, span_id);
		else for (let i of input_id) rem(i[0], i[1]);
	};
	const checkUsername = async (event: string | Event) => {
		let username = '';
		if (typeof event !== 'string') username = (event.target as HTMLInputElement).value;
		if (filterUsername(username) !== username) {
			showMessage('username', {
				text: 'Only text and underscore is allowed! ❌',
				variant: 'danger'
			});
			dataset.username = '';
			return 0;
		}
		if (interval) clearTimeout(interval);
		interval = setTimeout(async () => {
			showMessage(
				'username',
				{
					text: 'checking username...',
					variant: 'alert',
					cssClass: 'spinner'
				},
				false
			);
			await axios
				.get('/api/_users/', { params: { username } })
				.then((response) => {
					removeMessage('#username', '.message.alert.spinner');
					if (response.data.user === 0) dataset.username = username;
					else dataset.username = '';
					showMessage(
						'username',
						{
							text: response.data.user === 0 ? 'username available ✔' : 'username not available',
							variant: response.data.user === 0 ? 'success' : 'alert'
						},
						false
					);
				})
				.catch((error) => {
					message = { message: error, variant: 'danger' };
					console.error(error);
				});
		}, 800);
	};
	const handelForm = async (event: SubmitEvent) => {
		removeMessage([
			['#email', '.message'],
			['#fullname', '.message'],
			['#password', '.message'],
			['#re-pass', '.message']
		]);
		let username = event.target['username'].value;
		let fullname = event.target['fullname'].value;
		let email = event.target['email'].value;
		let passion = event.target['passion'].value;
		let password = event.target['password'].value;
		let repassword = event.target['re-pass'].value;
		let avatar = event.target['avatar'].files[0];
		if (fullname === '' || fullname.length < 4) {
			showMessage('fullname', { text: 'Please enter your fullname!', variant: 'alert' });
			return 0;
		}
		if (username !== dataset.username) checkUsername(username);
		if (email === '') {
			showMessage('email', { text: 'Please enter email address!', variant: 'alert' });
			return 0;
		}
		if (password === '' || password.length < 8) {
			showMessage('password', { text: 'Enter password more than 8 chars.', variant: 'danger' });
			return 0;
		}
		if (password !== repassword) {
			showMessage('re-pass', { text: 'Your entered password is not matching!', variant: 'danger' });
			return 0;
		}
		dataset.email = email;
		dataset.fullname = fullname;
		dataset.passion = passion;
		dataset.password = password;
		if (avatar) dataset.avatar = avatar;
		await save_form();
	};
	const save_form = async () => {
		console.log(dataset)
		const form = createForm(dataset);
		message = false
		await axios
			.post('/api/_users/', form, {
				headers: {
					request: 'sign_up'
				}
			})
			.then((res: any) => {
				res = res.data;
				if (res.success === 0) 
					message = {message: res.message, variant: 'danger'}
				if(res.success === 1){
					message = {message: res.message, variant: 'success'}
					Cookies.set('user', JSON.stringify(res.user))
				}
			})
			.catch((error) => {
				if (error.response.status === 422) {
					console.error(error.response.data.message);
					message = {message: error.response.data.message, variant: 'danger'}
				}
				else console.error(error.message)
			});
	};
	const handleProfile = (ev: Event) => {
		const img = (ev.target as HTMLInputElement).files[0];
		const reader = new FileReader();
		reader.onload = (event) => {
			const contents: any = event.target.result;
			const viewer: any = document.getElementById('image-view');
			const img = document.createElement('img') as HTMLImageElement;
			img.src = contents;
			viewer.innerHTML = '';
			viewer.appendChild(img);
		};
		reader.readAsDataURL(img);
	};
</script>

<div class="form">
	<h3>BECOME A {WEBSITE_NAME} MEMBER</h3>
	<h5>
		Create your {WEBSITE_NAME} Member profile and get full access to our products and buy things, Inspiration
		and community.
	</h5>
	<form on:submit|preventDefault={handelForm}>
		<div class="flex">
			<div class="flx-col">
				<button
					id="image-view"
					class="profile"
					on:click={() => document.getElementById('avatar').click()}
				>
					<Icon icon="teenyicons:user-outline" />
					<span>Browse</span>
				</button>
				<input on:change={handleProfile} type="file" id="avatar" />
			</div>

			<div class="flx-col">
				<label for="username">Enter Username</label>
				<input type="text" on:keyup={checkUsername} id="username" placeholder="E.g. littlezabi_" />
			</div>
		</div>
		<div class="flex">
			<div class="flx-col">
				<label for="fullname">Your full name</label>
				<input type="text" id="fullname" placeholder="E.g. John Doe" />
			</div>

			<div class="flx-col">
				<label for="email">Enter email address</label>
				<input type="text" id="email" placeholder="E.g. example123@abc.com" />
			</div>
		</div>
		<div class="flex">
			<div class="flx-col fw">
				<label for="passion">Your Passion (optional)</label>
				<input type="text" id="passion" placeholder="E.g. JavaScript Programmer" />
			</div>
		</div>
		<div class="flex">
			<div class="flx-col">
				<label for="password">Enter your password</label>
				<input type="text" id="password" placeholder="choose a strong password" />
			</div>
			<div class="flx-col">
				<label for="re-pass">Re-enter your password</label>
				<input type="text" id="re-pass" placeholder="Type password again" />
			</div>
		</div>
		<div class="flex">
			<button type="submit" class="submit">Sign Up</button>
		</div>
		{#if message} 
		<div class='message {message.variant}'>{message.message}</div>
		{/if}
	</form>
</div>

<style lang="scss">
	#avatar {
		display: none;
	}
	:global(.form .profile svg) {
		width: 20px;
		height: 20px;
	}
	:global(.form .profile img) {
		width: 100%;
		height: 100%;
		object-fit: cover;
		border-radius: 50%;
	}
	.profile {
		width: 60px;
		height: 60px;
		display: flex;
		border: 2px solid #ffcfea40;
		border-radius: 50%;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: none;
		font-size: 9px;
		color: rgb(225, 225, 225);
		cursor: pointer;
		padding: 0;
		margin: 0;
		overflow: hidden;
		& span {
			margin-top: 3px;
		}
	}
	:global(.spinner) {
		position: relative;
		&:after {
			position: absolute;
			content: '';
			width: 15px;
			height: 15px;
			border-radius: 50%;
			border: 2px solid rgba(250, 250, 250, 0.176);
			border-left-color: rgb(255, 0, 153);
			margin-left: 10px;
			animation: rotateSpinner 600ms linear forwards infinite;
			@keyframes rotateSpinner {
				100% {
					transform: rotate(360deg);
				}
			}
		}
	}
	.submit {
		width: 250px;
		height: 40px;
		margin: auto;
		cursor: pointer;
		border-radius: 1px;
		background: none;
		margin-top: 10px;
		color: white;
		border: 2px solid rgba(255, 255, 255, 0.595);
		transition: 300ms;
		&:hover {
			background: white;
			color: black;
		}
	}
	.form {
		font-family: 'JetBrainsMono Nerd Font', consolas;
	}
	input,
	button {
		outline: none;
		font-family: inherit;
	}
	.flx-col {
		display: flex;
		flex-direction: column;
		position: relative;
		& label {
			margin-bottom: 8px;
			margin-top:8px;
			color: rgb(221, 221, 221);
		}
		width: 100%;
		& input {
			width: 85%;
			height: 21px;
			padding-left: 8px;
			border: none;
			border-bottom: 1px solid #ffffff21;
			background: none;
			position: relative;
			color: white;
			font-size: 14px;
			transition: 300ms;
			&::placeholder {
				color: rgb(191, 191, 191);
			}
			&:hover,
			&:focus {
				border-bottom-color: rgb(255, 0, 89);
			}
		}
		&.fw {
			& input {
				width: 93%;
			}
		}
	}
	.flex {
		margin-top: 15px;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	h3 {
		text-transform: uppercase;
		font-size: 20px;
		font-weight: 600;
	}
	h5 {
		margin-top: 6px;
		font-size: 14px;
	}
	.form {
		margin: auto;
		max-width: 700px;
		padding: 10px;
	}
</style>
