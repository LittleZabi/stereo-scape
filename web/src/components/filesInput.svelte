<script lang="ts">
	import Icon from '@iconify/svelte';
	import axios from 'axios';
	import { slide } from 'svelte/transition';
	import { BACKEND_ } from '../lib/config';
	import { io } from 'socket.io-client';
	import { onMount } from 'svelte';
	import { userContext, imagesContext, updateImages, SettingsContext } from '../lib/store';
	import Process from './pnrs-graph.svelte';
	// @ts-ignore
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	let message = undefined;
	let processStarted = false;
	let ready = false;
	let estimate_time = 0;
	let nerfRes = { iteration: 0, image: false };
	let seriesData: [number?, number?][] = [];
	let process: { [key: string]: { title: string; progress: number } } = {};
	let est_intr = undefined;
	let new_est_time = 0;
	// let output_video = false;
	const showRemainingTime = (time: number) => {
		const hr = Math.floor(time / 3600);
		const min = Math.floor((time % 3600) / 60);
		const sec = (time % 60).toFixed(0);
		let f = '';
		if (hr) f += `${hr} hrs `;
		if (min) f += `${min} min `;
		if (sec) f += `${sec} sec`;
		return f;
	};
	const estimate_time_interval = () => {
		new_est_time = estimate_time;
		if (!new_est_time) return 0;
		if (est_intr) {
			clearInterval(est_intr);
		}
		est_intr = setInterval(() => {
			if (new_est_time <= 0) {
				new_est_time = 0;
				clearInterval(est_intr);
			} else {
				new_est_time = Math.abs(new_est_time - 1);
			}
		}, 1000);
	};
	$: estimate_time, estimate_time_interval();
	const handleFileInput = async (ev: any) => {
		message = false;
		let f = ev.target.files;
		let files = [...$imagesContext];
		if (files.length === 1 && files[0].type === 'video/mp4') files = [];
		if (!files.length) {
			let k = [];
			for (let file of f) {
				const isVideo = file.type === 'video/mp4';
				if (isVideo) {
					k = [file];
					break;
				} else {
					k.push(file);
				}
			}
			updateImages(k);
			return 0;
		}
		for (let i = 0; i < f.length; i++) {
			let item = f[i];
			const isVideo = item.type === 'video/mp4';
			if (isVideo) {
				files = [item];
				break;
			}
			let isExist = false;
			files.map((f: any) => {
				if (f.name === item.name) {
					isExist = true;
					return 0;
				}
			});
			if (!isExist) files.push(item);
		}
		console.log('files: ', files);
		updateImages(files);
	};
	let socket: any = undefined;
	const initSocket = async () => {
		socket = io('http://localhost:5000', {
			// @ts-ignore
			'connect timeout': 10000
		});
		socket.on('connect', () => {
			message = false;
		});
		socket.on('connect_error', (error) => {
			message = { message: 'Flask server is offline!', variant: 'danger' };
		});
		socket.on('error', (error) => {
			message = { message: `Error on sockets: ${error}`, variant: 'danger' };
		});
		socket.on('process_complete', (res) => {
			message = { message: 'Process completed!' };
			estimate_time = 0;
			new_est_time = 0;
			// output_video = res.video;
			if (est_intr) clearInterval(est_intr);
			processStarted = false;
		});
		socket.on('process_stop', (res) => {
			message = { message: res.message ? res.message : 'Process is stopped!', variant: 'alert' };
			processStarted = false;
		});
		socket.on('result', (res) => {
			nerfRes = res;
		});
		socket.on('progress', (res) => {
			if (res.process === 'generating_video') if (est_intr) clearInterval(est_intr);
			if (res.message) message = { message: res.message, variant: 'alert' };
			if (res.estimate_time) {
				estimate_time = res.estimate_time;
			}
			if (res.training)
				seriesData = [...seriesData, [Number(res.training.iteration), Number(res.training.psnr)]];
			process = {
				...process,
				[res.process]: { title: res.title, progress: Number(res.progress).toFixed(1) }
			};
		});
	};
	const stopProcess = () => {
		if (!processStarted) return;
		message = { message: 'Stopping process.....', variant: 'alert' };
		socket.emit('stop_process', { process: false });
		estimate_time = 0;
		new_est_time = 0;
		if (est_intr) clearInterval(est_intr);
	};
	onMount(async () => {
		await initSocket();
	});
	const startProcess = async () => {
		if (processStarted) return;
		seriesData = [];
		message = false;
		if (!$userContext || $userContext.id === undefined) {
			message = { message: 'Please login to start process!', variant: 'danger' };
			return 0;
		}
		const form = new FormData();
		for (let file of $imagesContext)
			form.append(`f_${String(Math.floor(Math.random() * 99999))}`, file);
		form.append('user', $userContext.id);
		let settings = $SettingsContext;
		delete settings.isOpened;
		form.append('config', JSON.stringify(settings));
		processStarted = true;
		await axios
			.post(BACKEND_ + '/files', form, {
				onUploadProgress: (progressEvent) => {
					process = {
						uploading_files: {
							title: 'Uploading Images',
							progress: Math.round((progressEvent.loaded / progressEvent.total) * 100)
						}
					};
				}
			})
			.then((response) => {
				const res = response.data;
				if (res.error && res.error != '') {
					message = { message: res.message, variant: 'danger' };
				}
			})
			.catch((error) => console.error(error));
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
	function dropHandler(ev: any) {
		dropLeave(ev);
		message = false;
		ev.preventDefault();
		let files = [...$imagesContext];
		if (files.length === 1 && files[0].type === 'video/mp4') files = [];
		console.log(files);
		if (ev.dataTransfer.items) {
			for (let item of [...ev.dataTransfer.items]) {
				const file = item.getAsFile();
				const isVideo = item.type === 'video/mp4';
				if (isVideo) {
					files = [file];
					break;
				}
				if (item.kind === 'file') {
					let isExist = false;
					$imagesContext.map((f: any) => {
						if (f.name === file.name) {
							isExist = true;
							return 0;
						}
					});
					if (!isExist) files.push(file);
				}
			}
		} else {
			for (let file of [...ev.dataTransfer.files]) {
				const isVideo = file.type === 'video/mp4';
				if (isVideo) {
					files = [file];
					break;
				}
				files.push(file);
			}
		}
		updateImages(files);
	}
	let selectedFileIndex = null;
	const removeFile = () => {
		if (selectedFileIndex) {
			$imagesContext.splice(selectedFileIndex, 1);
			const files = [...$imagesContext];
			updateImages(files);
		} else {
			message = { message: 'No file selected!', variant: 'alert' };
		}
	};
	const showFile = () => {
		const file = $imagesContext[selectedFileIndex];
		const reader = new FileReader();
		reader.onload = (event) => {
			const contents = event.target.result;
			const viewer: any = document.getElementById('image-view');
			viewer.src = contents;
		};
		reader.readAsDataURL(file);
	};
	const clearAll = () => {
		updateImages([]);
		process = {};
		message = false;
	};
	const selectFile = (e: any) => {
		if (e.target.value != 'none') {
			selectedFileIndex = parseInt(e.target.value);
			showFile();
		}
	};
</script>

{#if ready}
	<h3>Images is ready</h3>
	<p class="x23">
		Click on start process button to start. before starting make sure you select same object images.
	</p>
{:else}
	<h3>Upload your images or video ✅</h3>
	<p class="x23">Enter your images/video of object. only one video is supported of object. add images/video from different view points of object. ✔</p>
{/if}
{#if !$userContext || $userContext.id === undefined}
	<p style="margin-bottom: 10px;" class="message danger">User is not logged! please login first</p>
{/if}

{#if ready}
	<div class="_flex ready_" style="justify-content: space-between">
		<div class="xz">
			<h4>{$imagesContext.length} images is ready</h4>
			{#if !processStarted}
				<button class="snd" on:click={() => (ready = false)}>Browse images</button>
			{/if}
			{#each Object.keys(process) as proc}
				<div class="prog-wrap">
					<h5>{process[proc].title} {process[proc].progress}%</h5>
					<div class="prog-out">
						<div class="progress" style={`width: ${process[proc].progress}%`}></div>
					</div>
				</div>
			{/each}
		</div>
		<div class="xy">
			<div class="_flex yt">
				<div class="chart">
					<Process {seriesData} />
				</div>
				{#if nerfRes.image}
					<div class="output" transition:slide={{ axis: 'x' }}>
						<p>Result {nerfRes.iteration} / {$SettingsContext.n_iterations} Iterations</p>
						<img src={PUBLIC_BACKEND_URL + nerfRes.image} id="result" alt="" />
					</div>
				{/if}
				<!-- {#if output_video}
					<div transition:slide={{ axis: 'x' }}>
						<video
							autoplay
							muted
							loop
							controls
							class="vid-x"
							src={PUBLIC_BACKEND_URL + output_video}
						>
							<track kind="captions" />
						</video>
					</div>
				{/if} -->
			</div>
			<button
				class="snd snd1 {processStarted ? 'active' : ''}"
				style="margin-top:10px;"
				on:click={startProcess}
			>
				<Icon icon="material-symbols-light:not-started-outline" style="color: #00ccff" />
				START
			</button>
			<button
				class="snd snd2 {!processStarted ? 'active' : ''}"
				style="margin-top:10px;"
				on:click={stopProcess}
			>
				<Icon icon="ic:round-stop" style="color: #ff0040" />
				STOP
			</button>

			{#if estimate_time}
				<span class="time-rem">
					{new_est_time ? `${showRemainingTime(new_est_time)} remaining` : ''}
				</span>
			{/if}
		</div>
	</div>
{:else}
	<div class="_flex">
		<div>
			<input
				type="file"
				id="fileInput"
				multiple
				accept="video/mp4, image/*"
				on:change={handleFileInput}
				style="display:none;"
			/>
			<div
				class="place"
				role="region"
				aria-labelledby="dropzone-label"
				on:drop={dropHandler}
				on:dragleave={dropLeave}
				on:dragover={dragOverHandler}
			>
				<div>
					<img src="/media/upload.png" alt="upload" />
					<h4 id="m3c2x99k">Drag and drop your images/video.</h4>
					<button on:click={() => document.getElementById('fileInput').click()}>Browse</button>
				</div>
			</div>
		</div>
		{#if $imagesContext.length}
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
						{#each $imagesContext as file, i}
							<option value={i}>
								{i + 1} - {file.name}
							</option>
						{/each}
					</select>
					<button class="x321" on:click={removeFile}>
						<Icon icon="solar:trash-bin-trash-broken" />
					</button>
				</div>
				<div class="image-viewer" style="display: {selectedFileIndex != null ? 'block' : 'none'}">
					<img src="" id="image-view" alt="" />
				</div>
				<button class="snd" on:click={() => (ready = !ready)}>Ready</button>
			</div>
		{/if}
	</div>
{/if}
{#if message}
	<div class="message {message.variant}">{message.message}</div>
{/if}

<style lang="scss">
	.vid-x {
		width: 221px;
		height: 175px;
		margin: 24px 0px 5px 9px;
		border-radius: 6px;
		object-fit: cover;
	}
	.time-rem {
		font-size: 14px;
		margin-left: 10px;
		width: 255px;
		display: inline-block;
	}
	.output {
		margin-left: 10px;
		& p {
			margin-bottom: 5px;
		}
		& img {
			width: 175px;
			height: 175px;
			border-radius: 4px;
		}
	}
	.ready_ {
		margin-top: 28px;
		& .xz {
			margin-right: 20px;
			& h4 {
				margin-bottom: 10px;
			}
			& button {
				border: none;
				padding: 0;
				width: max-content;
				height: max-content;
				color: dodgerblue;
				font-weight: bold;
				text-decoration: underline;
				&:hover {
					background: none;
					color: white !important;
				}
			}
		}
		& .xy {
			margin-left: 20px;
		}
	}
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
		height: 3px;
		width: 300px;
		background: #0000004f;
		border-radius: 18px;
		border: 1px solid #ffffff0f;
	}
	.progress {
		height: 100%;
		background: linear-gradient(45deg, #ff0052, #fb0079, #ff008b, #ff2b00);
		border-radius: 18px;
		transition: 300ms linear;
	}
	.snd {
		width: 100px;
		height: 40px;
		margin: auto;
		margin-right: 10px;
		margin-bottom: 10px;
		background: none;
		color: white;
		border: 2px solid #ffffff4a;
		border-radius: 3px;
		text-transform: uppercase;
		font-family: inherit;
		cursor: pointer;
		transition: 300ms;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		&.snd1 {
			background: #00ff9126;
			border-color: #00ff9126;
			&:hover {
				background: #00ff9136;
			}
		}
		&.snd2 {
			background: #ff006a4e;
			border-color: #ff006a4e;
			&:hover {
				background: #ff008c67;
			}
		}
		&.active {
			opacity: 0.3;
			&.snd1 {
				&:hover {
					background: #00ff9126;
				}
			}
			&.snd2 {
				&:hover {
					background: #ff006a4e;
				}
			}
		}
		// &:hover {
		// 	background: white;
		// 	color: black;
		// }
	}
	:global(.snd svg) {
		font-size: 28px;
		margin-right: 8px;
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
