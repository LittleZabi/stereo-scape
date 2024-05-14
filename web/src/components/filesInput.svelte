<script lang="js">
	import Icon from '@iconify/svelte';
	import axios from 'axios';
	import { slide } from 'svelte/transition';
	import { BACKEND_ } from '../lib/config';
	import { io } from 'socket.io-client';
	import { onMount } from 'svelte';

	let message = undefined 
	let files = [];
	let uploadedList = [];
	let flaskApiBaseUrl = 'hello world';
	let session_name = undefined;
	let processStarted = false;
	let process = {};
	const handleFileInput = async (ev) => {
		message = false;
		let f = ev.target.files;
		if (!files.length) {
			files = [...f];
			return 0;
		}
		for (let i = 0; i < f.length; i++) {
			let item = f[i];
			let isExist = false;
			files.map((f) => {
				if (f.name === item.name) {
					isExist = true;
					return 0;
				}
			});
			if (!isExist) files.push(item);
		}
		files = [...files];
	};
	let socket = undefined;
	const initSocket = async () => {
		socket = io('http://localhost:5000', {
			'connect timeout': 10000
		});
		socket.on('connect', () => {
			message = false;
			// console.log('socket created with ID: ', socket.id);
		});
		socket.on('connect_error', (error) => {
			message = {message: 'Flask server is offline!', variant: 'danger'}
		});
		socket.on('error', (error) => {
			console.error('Error on socket: ', error);
			message = {message: `Error on sockets: ${error}`, variant: 'danger'}
		});
		socket.on('progress', (res) => {
			process = { ...process, [res.process]: Math.floor(res.percent) };
		});
	};
	onMount(async () => {
		await initSocket();
	});
	const startProcess = async () => {
		if (processStarted) {
			message = {
				message: 'Process is already started so just wait for results',
				variant: 'alert'
			};
			return 0;
		}
		const form = new FormData();
		for (let file of files) {
			form.append(`f_${String(Math.floor(Math.random() * 99999))}`, file);
		}
		processStarted = true;
		await axios
			.post(BACKEND_ + '/files', form, {
				onUploadProgress: (progressEvent) => {
					process = {
						...process,
						'Uploading Images': Math.round((progressEvent.loaded / progressEvent.total) * 100)
					};
				}
			})
			.then((response) => {
				const res = response.data;
				console.log(res);
				if (res.error && res.error != '') {
					message = { message: res.message, variant: 'danger' };
				}
			})
			.catch((error) => console.error(error));
	};
	const sendToTheServer = async () => {
		let api_url = `${flaskApiBaseUrl}/resize/`;
		const formData = new FormData();
		formData.append('session_name', session_name);
		// formData.append('user', data.user ? data.user.object._id : '');
		for (let file of files) {
			console.log(file);
			return 0;
			formData.append(`${String(Math.floor(Math.random() * 99999))}`, file.content);
			formData.append(`filesize`, file.filesize);
			formData.append(`width`, file.width);
			formData.append(`height`, file.height);
			await axios
				.post(api_url, formData, {
					headers: {
						'Content-Type': 'multipart/form-data'
					}
				})
				.then(async (res) => {
					let response = res.data;
					session_name = response.session_name;
					console.log(res.data);
				})
				.catch((e) => {
					message = {
						message: `Error: ${e.message}`,
						variant: 'error'
					};
				});
		}
	};
	const dropLeave = (event) => {
		event.target.classList.remove('active');
		try {
			let k = document?.getElementById('m3c2x99k');
			k.textContent = 'Drag one or more files to this';
		} catch (e) {}
	};
	function dragOverHandler(ev) {
		ev.preventDefault();
		ev.target.classList.add('active');
		try {
			let k = document?.getElementById('m3c2x99k');
			k.textContent = "Release to Upload File's";
		} catch (e) {}
	}
	function dropHandler(ev) {
		dropLeave(ev);
		message = false;
		ev.preventDefault();
		if (ev.dataTransfer.items) {
			[...ev.dataTransfer.items].forEach((item, i) => {
				if (item.kind === 'file') {
					const file = item.getAsFile();
					let isExist = false;
					files.map((f) => {
						if (f.name === file.name) {
							isExist = true;
							return 0;
						}
					});
					if (!isExist) files.push(file);
				}
			});
		} else {
			[...ev.dataTransfer.files].forEach((file, i) => files.push(file));
		}
		files = [...files];
	}
	let selectedFileIndex = null;
	const removeFile = () => {
		if(selectedFileIndex){
		files.splice(selectedFileIndex, 1);
		files = [...files];
		}else{
			message = {message: 'No file selected!', variant: 'alert'}
		}
	};
	const showFile = () => {
		const file = files[selectedFileIndex];
		const reader = new FileReader();
		reader.onload = (event) => {
			const contents = event.target.result;
			const viewer = document.getElementById('image-view');
			viewer.src = contents;
		};
		reader.readAsDataURL(file);
	};
	const clearAll = () => (files = []);
	const selectFile = (e) => {
		if (e.target.value != 'none') {
			selectedFileIndex = parseInt(e.target.value);
			showFile();
		}
	};
</script>

<h3>Upload your images ✅</h3>
<p class="x23">Enter your images of a object from different view points. ✔</p>
<div class="_flex">
	<div>
		{#if Object.keys(process).length}
			{#each Object.keys(process) as proc}
				<div class="prog-wrap">
					<h5>{proc} {process[proc]}%</h5>
					<div class="prog-out">
						<div class="progress" style={`width: ${process[proc]}%`}></div>
					</div>
				</div>
			{/each}
		{:else}
			<input
				type="file"
				id="fileInput"
				multiple
				accept="image/*"
				on:change={handleFileInput}
				style="display:none;"
			/>
			<div
				class="place"
				aria-label="buttons"
				aria-roledescription="drag and drop your elements into this container"
				aria-dropeffect="execute"
				on:drop={dropHandler}
				on:dragleave={dropLeave}
				on:dragover={dragOverHandler}
			>
				<div>
					<img src="/media/upload.png" alt="upload" />
					<h4 id="m3c2x99k">Drag and drop your images.</h4>
					<button on:click={() => document.getElementById('fileInput').click()}>Browse</button>
				</div>
			</div>
		{/if}
	</div>
	{#if files.length}
		<div class="right" transition:slide={{ axis: 'x' }}>
			<div class="c2z">
				<h4>Files list</h4>
				<button class="x32" on:click={() => clearAll()}>
					<span>Clear All</span>
					<Icon icon="solar:trash-bin-trash-broken" />
				</button>
			</div>
			<div class="ovx">
				<select class="select" on:change={selectFile}>
					<option value="none">Select image to show</option>
					{#each files as file, i}
						<option value={i}>
							{i + 1} - {file.name}
						</option>
					{/each}
				</select>
				<button class="x321" on:click={removeFile}>
					<Icon icon="solar:trash-bin-trash-broken" />
				</button>
			</div>
			<div class="image-viewer" style="display: {selectedFileIndex ? 'block' : 'none'}">
				<img src="" id="image-view" alt="" />
			</div>
			<button class="snd" on:click={startProcess}>Start Process</button>
		</div>
	{/if}
</div>
{#if message}
	<div class="message {message.variant}">{message.message}</div>
{/if}
<style lang="scss">
	.image-viewer {
		margin-bottom: 13px;
		& img {
			width: 100%;
			height: 151px;
			object-fit: contain;
		}
	}
	.select {
		width: 250px;
		margin: 10px 10px 0 10px;
		height: 40px;
		border-radius: 28px;
		background: #090918;
		outline: none;
		border: 2px solid white;
		padding: 0 8px;
		cursor: pointer;
		color: white;
		& option {
			color: white;
			background: #090918;
		}
	}
	.prog-wrap {
		margin: 20px auto 5px auto;
		& h5 {
			margin-bottom: 5px;
		}
	}
	.prog-out {
		display: flex;
		height: 10px;
		width: 600px;
		background: #0000004f;
		border-radius: 18px;
		border: 1px solid #ffffff0f;
	}
	.progress {
		height: 100%;
		background: linear-gradient(45deg, #b400ff, #0066ff, #00ffff);
		border-radius: 18px;
		transition: 300ms linear;
	}
	.snd {
		width: 250px;
		height: 40px;
		margin: auto;
		margin-bottom: 10px;
		background: none;
		color: white;
		border: 2px solid #ffffff4a;
		border-radius: 3px;
		text-transform: uppercase;
		font-family: inherit;
		cursor: pointer;
		transition: 300ms;
		&:hover {
			background: white;
			color: black;
		}
	}
	:global(.c2z button svg) {
		font-size: 16px;
	}
	.c2z {
		display: flex;
		justify-content: space-between;
		align-items: center;
		& h4 {
			font-size: 18px;
		}
		& button {
			display: flex;
			align-items: center;
			border: none;
			border-bottom: 2px solid #ff002f;
			background: none;
			color: white;
			font-family: inherit;
			padding-bottom: 4px;
			cursor: pointer;
			transition: 300ms;
			&:hover {
				color: #ff5e7c !important;
			}
			& span {
				margin-right: 8px;
			}
		}
	}
	.right {
		margin-left: 40px;
		max-height: 400px;
		& .ovx {
			margin-top: 10px;
			margin-bottom: 30px;
			width: 100%;
			display: flex;
			align-items: center;
			justify-content: center;
		}
	}
	.x32 {
		font-size: 16px;
	}
	.x321 {
		background: none;
		border: none;
		margin-top: 10px;
		color: #ff0015;
		&:hover {
			color: #e600ff;
		}
		font-size: 22px;
		cursor: pointer;
	}
	h3 {
		font-size: 22px;
		margin: 5px 0px 0px 0px;
	}
	.x23 {
		margin-bottom: 10px;
		font-size: 14px;
		margin-top: 5px;
	}

	._flex {
		display: flex;
	}
	.place {
		width: 400px;
		height: 300px;
		display: flex;
		align-items: center;
		justify-content: center;
		border: 2px dashed grey;
		border-radius: 18px;
		text-align: center;
		&.active {
			border-color: #00e6ff;
		}
		& h4 {
			margin-bottom: 10px;
			color: grey;
		}
		& button {
			width: 250px;
			height: 40px;
			background: none;
			border: 2px solid rgb(133, 133, 133);
			color: white;
			border-radius: 25px;
			cursor: pointer;
			transition: all 300ms ease-in;
			font-family: inherit;
			&:hover {
				background: white;
				color: black;
			}
		}
		& img {
			width: 40px;
			filter: invert(1);
		}
	}
</style>
