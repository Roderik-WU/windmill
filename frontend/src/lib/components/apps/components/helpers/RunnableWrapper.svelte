<script lang="ts">
	import { getContext, onMount } from 'svelte'
	import type { AppInput } from '../../inputType'
	import type { Output } from '../../rx'
	import type { AppViewerContext, ListContext } from '../../types'
	import { isScriptByNameDefined, isScriptByPathDefined } from '../../utils'
	import NonRunnableComponent from './NonRunnableComponent.svelte'
	import RunnableComponent from './RunnableComponent.svelte'
	import { sendUserToast } from '$lib/toast'
	import InitializeComponent from './InitializeComponent.svelte'
	import type { CancelablePromise } from '$lib/gen'

	type SideEffectAction =
		| {
				selected:
					| 'gotoUrl'
					| 'none'
					| 'setTab'
					| 'sendToast'
					| 'sendErrorToast'
					| 'errorOverlay'
					| 'openModal'
					| 'closeModal'
					| 'open'
					| 'close'
					| 'clearFiles'
					| 'downloadFile'
				configuration: {
					gotoUrl: { url: (() => string) | string | undefined; newTab: boolean | undefined }
					setTab: {
						setTab:
							| (() => { id: string; index: number }[])
							| { id: string; index: number }[]
							| undefined
					}
					sendToast?: {
						message: (() => string) | string | undefined
					}
					sendErrorToast?: {
						message: (() => string) | string | undefined
						appendError: boolean | undefined
					}
					openModal?: {
						modalId: string | undefined
					}
					closeModal?: {
						modalId: string | undefined
					}
					open?: {
						id: string | undefined
					}
					close?: {
						id: string | undefined
					}
					clearFiles?: {
						id: string | undefined
					}
					downloadFile?: {
						s3FileInput: (() => string | { s3: string; storage?: string }) | string | { s3: string; storage?: string } | undefined
						fileName: (() => string) | string | undefined
					}
				}
		  }
		| undefined

	interface Props {
		componentInput: AppInput | undefined
		noInitialize?: boolean
		hideRefreshButton?: boolean | undefined
		overrideCallback?: (() => CancelablePromise<void>) | undefined
		overrideAutoRefresh?: boolean
		replaceCallback?: boolean
		id: string
		result?: any
		initializing?: boolean | undefined
		loading?: boolean
		extraQueryParams?: Record<string, any>
		autoRefresh?: boolean
		runnableComponent?: RunnableComponent | undefined
		forceSchemaDisplay?: boolean
		runnableClass?: string
		runnableStyle?: string
		doOnSuccess?: SideEffectAction
		doOnSubmit?: SideEffectAction
		doOnError?: SideEffectAction
		render: boolean
		recomputeIds?: string[]
		outputs: {
			result: Output<any>
			loading: Output<boolean>
			jobId?: Output<any> | undefined
		}
		extraKey?: string | undefined
		refreshOnStart?: boolean
		errorHandledByComponent?: boolean
		allowConcurentRequests?: boolean
		onSuccess?: (result: any) => void
		children?: import('svelte').Snippet
		nonRenderedPlaceholder?: import('svelte').Snippet
		preventDefaultRefresh?: boolean
	}

	let {
		componentInput = $bindable(),
		noInitialize = false,
		hideRefreshButton = undefined,
		overrideCallback = undefined,
		overrideAutoRefresh = false,
		replaceCallback = false,
		id,
		result = $bindable(undefined),
		initializing = $bindable(undefined),
		loading = $bindable(false),
		extraQueryParams = {},
		autoRefresh = true,
		runnableComponent = $bindable(undefined),
		forceSchemaDisplay = false,
		runnableClass = '',
		runnableStyle = '',
		doOnSuccess = undefined,
		doOnSubmit = undefined,
		doOnError = undefined,
		render,
		recomputeIds = [],
		outputs,
		extraKey = undefined,
		refreshOnStart = false,
		errorHandledByComponent = false,
		allowConcurentRequests = false,
		onSuccess = () => {},
		children,
		nonRenderedPlaceholder
	}: Props = $props()

	$effect.pre(() => {
		if (initializing == undefined) {
			initializing = true
		}
	})

	export function setArgs(value: any) {
		runnableComponent?.setArgs(value)
	}

	const { staticExporter, initialized, noBackend, componentControl, runnableComponents } =
		getContext<AppViewerContext>('AppViewerContext')
	const iterContext = getContext<ListContext>('ListWrapperContext')
	const rowContext = getContext<ListContext>('RowWrapperContext')

	if (noBackend && componentInput?.type == 'runnable') {
		result = componentInput?.['value']
	}

	if (noBackend) {
		initializing = false
	}

	onMount(() => {
		$staticExporter[id] = () => {
			return result
		}
	})

	const fullId = id + (extraKey ?? '')
	if (!(initializing && componentInput?.type === 'runnable' && isRunnableDefined(componentInput))) {
		initializing = false
	} else {
		if (
			(initializing == undefined || initializing == true) &&
			Object.keys($initialized?.runnableInitialized ?? {}).includes(fullId)
		) {
			initializing = false
		}

		if (
			result == undefined &&
			!initializing &&
			iterContext == undefined &&
			rowContext == undefined
		) {
			result = $initialized.runnableInitialized?.[fullId]
		}
	}

	// We need to make sure that old apps have correct values. Triggerable (button, form, etc) have both autoRefresh and recomputeOnInputChanged set to false
	$effect.pre(() => {
		if (!autoRefresh && componentInput?.type === 'runnable' && componentInput.autoRefresh) {
			componentInput.autoRefresh = false
			componentInput.recomputeOnInputChanged = false
		}
	})

	function isRunnableDefined(componentInput) {
		return (
			(isScriptByNameDefined(componentInput) &&
				componentInput.runnable.inlineScript != undefined) ||
			isScriptByPathDefined(componentInput)
		)
	}

	async function handleSubmitSideEffect() {
		if (!doOnSubmit) return

		if (doOnSubmit.selected == 'none') return

		await executeSideEffect(doOnSubmit, true)
	}

	export async function handleSideEffect(success: boolean, errorMessage?: string) {
		const sideEffect = success ? doOnSuccess : doOnError

		if (recomputeIds && success) {
			recomputeIds.forEach((id) => $runnableComponents?.[id]?.cb.map((cb) => cb()))
		}
		if (!sideEffect) return

		if (sideEffect.selected == 'none') return

		await executeSideEffect(sideEffect, success, errorMessage)
	}

	async function executeSideEffect(sideEffect: SideEffectAction, success: boolean = true, errorMessage?: string) {
		if (!sideEffect) return

		switch (sideEffect.selected) {
			case 'setTab':
				let setTab = sideEffect?.configuration.setTab?.setTab
				if (!setTab) return
				if (typeof setTab === 'function') {
					setTab = await setTab()
				}
				if (Array.isArray(setTab)) {
					setTab.forEach((tab) => {
						if (tab) {
							const { id, index } = tab
							$componentControl[id].setTab?.(index)
						}
					})
				}
				break
			case 'gotoUrl':
				let gotoUrl = sideEffect?.configuration?.gotoUrl?.url

				if (!gotoUrl) return
				if (typeof gotoUrl === 'function') {
					gotoUrl = await gotoUrl()
				}
				const newTab = sideEffect?.configuration?.gotoUrl?.newTab

				if (newTab) {
					window.open(gotoUrl, '_blank')
				} else {
					window.location.href = gotoUrl
				}

				break
			case 'sendToast': {
				let message = sideEffect?.configuration?.sendToast?.message

				if (!message) return
				if (typeof message === 'function') {
					message = await message()
				}
				sendUserToast(message, !success)
				break
			}
			case 'sendErrorToast': {
				let message = sideEffect?.configuration?.sendErrorToast?.message
				const appendError = sideEffect?.configuration?.sendErrorToast?.appendError

				if (!message) return

				if (typeof message === 'function') {
					message = await message()
				}

				sendUserToast(message, true, [], appendError ? errorMessage : undefined)
				break
			}
			case 'openModal': {
				const modalId = sideEffect?.configuration?.openModal?.modalId
				if (modalId) {
					$componentControl[modalId].openModal?.()
				}
				break
			}
			case 'closeModal': {
				const modalId = sideEffect?.configuration?.closeModal?.modalId

				if (!modalId) return

				$componentControl[modalId].closeModal?.()
				break
			}
			case 'open': {
				const id = sideEffect?.configuration?.open?.id

				if (!id) return

				$componentControl[id].open?.()
				break
			}
			case 'close': {
				const id = sideEffect?.configuration?.close?.id

				if (!id) return

				$componentControl[id].close?.()
				break
			}
			case 'clearFiles': {
				const id = sideEffect?.configuration?.clearFiles?.id

				if (!id) return

				$componentControl[id].clearFiles?.()
				break
			}
			case 'downloadFile': {
				let s3FileInput = sideEffect?.configuration?.downloadFile?.s3FileInput
				let fileName = sideEffect?.configuration?.downloadFile?.fileName

				if (!s3FileInput) return

				if (typeof s3FileInput === 'function') {
					s3FileInput = await s3FileInput()
				}
				if (typeof fileName === 'function') {
					fileName = await fileName()
				}

				try {
					const handleError = (error: Error) => {
						console.error('Error downloading file:', error)
						sendUserToast(
							`Error downloading file: ${error.message}. Ensure it is a valid URL, a base64 encoded data URL (data:...), or a valid S3 object.`,
							true
						)
					}

					const isBase64 = (str: string) => {
						try {
							return btoa(atob(str)) === str
						} catch (err) {
							return false
						}
					}

					const downloadFile = (url: string, downloadFilename?: string) => {
						const link = document.createElement('a')
						link.href = url
						link.download = downloadFilename || 'download'
						link.target = '_blank'
						link.rel = 'external'
						document.body.appendChild(link)
						link.click()
						document.body.removeChild(link)
					}

					if (typeof s3FileInput === 'object' && 's3' in s3FileInput) {
						const workspaceId = ($appViewerContext as any)?.workspace
						const s3href = `/api/w/${workspaceId}/job_helpers/download_s3_file?file_key=${encodeURIComponent(
							s3FileInput?.s3 ?? ''
						)}${s3FileInput?.storage ? `&storage=${s3FileInput.storage}` : ''}`
						downloadFile(s3href, fileName || s3FileInput.s3)
					} else if (typeof s3FileInput === 'string') {
						if (s3FileInput.startsWith('data:')) {
							downloadFile(s3FileInput, fileName)
						} else if (isBase64(s3FileInput)) {
							const base64Url = `data:application/octet-stream;base64,${s3FileInput}`
							downloadFile(base64Url, fileName)
						} else if (/^(http|https):\/\//.test(s3FileInput) || s3FileInput.startsWith('/')) {
							const url = s3FileInput.startsWith('/')
								? `${window.location.origin}${s3FileInput}`
								: s3FileInput
							downloadFile(url, fileName ?? s3FileInput.split('/').pop()?.split('?')[0])
						} else {
							handleError(
								new Error(
									'The input must be a valid URL, a base64 encoded string, or a valid S3 object.'
								)
							)
						}
					} else {
						handleError(
							new Error('The input must be a string or an object with an s3 property.')
						)
					}
				} catch (error) {
					console.error('Error downloading file:', error)
					sendUserToast(`Error downloading file: ${error}`, true)
				}
				break
			}
			default:
				break
		}
	}
</script>

{#if componentInput === undefined}
	{#if !noInitialize}
		<InitializeComponent {id} />
	{/if}
	{#if render}
		{@render children?.()}
	{:else}
		{@render nonRenderedPlaceholder?.()}
	{/if}
{:else if componentInput.type === 'runnable' && isRunnableDefined(componentInput)}
	<RunnableComponent
		{noInitialize}
		{allowConcurentRequests}
		{refreshOnStart}
		{extraKey}
		{replaceCallback}
		bind:loading
		bind:this={runnableComponent}
		fields={componentInput.fields}
		bind:result
		runnable={componentInput.runnable}
		hideRefreshButton={hideRefreshButton ?? componentInput.hideRefreshButton}
		transformer={componentInput.transformer}
		{autoRefresh}
		{overrideCallback}
		{overrideAutoRefresh}
		recomputableByRefreshButton={componentInput.autoRefresh ?? true}
		recomputeOnInputChanged={componentInput.recomputeOnInputChanged}
		{id}
		{extraQueryParams}
		{forceSchemaDisplay}
		{initializing}
		wrapperClass={runnableClass}
		wrapperStyle={runnableStyle}
		{render}
		on:started={(e) => {
			handleSubmitSideEffect()
		}}
		on:done
		on:doneError
		on:cancel
		on:recompute
		on:argsChanged
		on:resultSet={(e) => {
			const res = e.detail
			if ($initialized?.runnableInitialized?.[fullId] === undefined) {
				$initialized.runnableInitialized = {
					...($initialized.runnableInitialized ?? {}),
					[fullId]: res
				}
			}

			initializing = false
		}}
		on:success={(e) => {
			onSuccess(e.detail)
			handleSideEffect(true)
		}}
		on:handleError={(e) => handleSideEffect(false, e.detail)}
		{outputs}
		{errorHandledByComponent}
		{nonRenderedPlaceholder}
	>
		{@render children?.()}
	</RunnableComponent>
{:else}
	<NonRunnableComponent
		{nonRenderedPlaceholder}
		{noInitialize}
		{render}
		bind:result
		{id}
		{componentInput}
	>
		{@render children?.()}
	</NonRunnableComponent>
{/if}
