<script lang="ts">
	import Modal2 from '../common/modal/Modal2.svelte'
	import { superadmin, workspaceStore } from '$lib/stores'
	import Notification from '../common/alert/Notification.svelte'
	import Button from '../common/button/Button.svelte'
	import { Trash2, Play, Filter, Search, Mailbox } from 'lucide-svelte'
	import Skeleton from '../common/skeleton/Skeleton.svelte'
	import List from '../common/layout/List.svelte'
	import { fade } from 'svelte/transition'
	import { sendUserToast } from '$lib/toast'

	interface Props {
		updateUnreadCount?: (count: number) => void
	}

	let { updateUnreadCount = () => {} }: Props = $props()

	// Internal state
	let open = $state(false)
	let unreadCount = $state(0)

	// Mock MailboxMessage type until backend is ready
	interface MailboxMessage {
		message_id: number
		mailbox_id?: string
		workspace_id: string
		type: 'trigger' | 'debouncing_stale_data'
		created_at: string
		payload: any
	}

	// State
	let messages = $state<MailboxMessage[]>([])
	let loading = $state(false)
	let selectedMessages = $state(new Set<number>())
	let allSelected = $state(false)

	// Filter state
	let filterType = $state('')
	let filterMailboxId = $state('')
	let filterMessageId = $state('')

	// Pagination
	let currentPage = $state(1)
	let perPage = $state(20)
	let hasMore = $state(true)

	const columns = [
		{ field: 'message_id', header: 'ID', class: 'w-20' },
		{ field: 'type', header: 'Type', class: 'w-32' },
		{ field: 'mailbox_id', header: 'Mailbox ID', class: 'w-40' },
		{ field: 'created_at', header: 'Created', class: 'w-40' },
		{ field: 'payload', header: 'Payload', class: 'w-96' },
		{ field: 'actions', header: 'Actions', class: 'w-32' }
	]

	// Refresh messages when modal opens
	$effect(() => {
		if (open && $superadmin) {
			refreshMessages()
		}
	})

	// Mock API service - replace with actual service when backend is ready
	async function mockApiCall(endpoint: string, options?: any): Promise<any> {
		console.warn(`Mock API call to ${endpoint} - implement backend MailboxService`)

		// Return mock data for testing
		if (endpoint.includes('list')) {
			return []
		}

		return { success: true }
	}

	async function refreshMessages() {
		if (!$workspaceStore) return

		loading = true
		try {
			const filters: any = {
				workspace: $workspaceStore,
				page: currentPage,
				perPage: perPage
			}

			if (filterType) filters.mailboxType = filterType
			if (filterMailboxId) filters.mailboxId = filterMailboxId
			if (filterMessageId) filters.messageId = parseInt(filterMessageId)

			// Use mock API for now
			const result = await mockApiCall('list', filters)
			messages = Array.isArray(result) ? result : []
			hasMore = messages.length === perPage
			updateUnreadCount(messages.length)
		} catch (error) {
			console.error('Failed to fetch mailbox messages:', error)
			sendUserToast('Failed to fetch mailbox messages', true)
		} finally {
			loading = false
		}
	}

	async function deleteMessage(messageId: number) {
		if (!$workspaceStore) return

		try {
			await mockApiCall(`delete/${messageId}`, {
				workspace: $workspaceStore,
				messageId
			})
			sendUserToast('Message deleted successfully')
			refreshMessages()
		} catch (error) {
			console.error('Failed to delete message:', error)
			sendUserToast('Failed to delete message', true)
		}
	}

	async function handleMessage(messageId: number) {
		if (!$workspaceStore) return

		try {
			await mockApiCall(`handle/${messageId}`, {
				workspace: $workspaceStore,
				messageId
			})
			sendUserToast('Message handled successfully')
			refreshMessages()
		} catch (error) {
			console.error('Failed to handle message:', error)
			sendUserToast('Failed to handle message', true)
		}
	}

	async function bulkDelete() {
		if (!$workspaceStore || selectedMessages.size === 0) return

		try {
			await mockApiCall('bulk_delete', {
				workspace: $workspaceStore,
				requestBody: {
					messageIds: Array.from(selectedMessages)
				}
			})
			sendUserToast(`Deleted ${selectedMessages.size} messages`)
			selectedMessages.clear()
			allSelected = false
			refreshMessages()
		} catch (error) {
			console.error('Failed to bulk delete messages:', error)
			sendUserToast('Failed to delete messages', true)
		}
	}

	function toggleMessageSelection(messageId: number) {
		if (selectedMessages.has(messageId)) {
			selectedMessages.delete(messageId)
		} else {
			selectedMessages.add(messageId)
		}
		selectedMessages = selectedMessages
		allSelected = selectedMessages.size === messages.length
	}

	function toggleAllSelection() {
		if (allSelected) {
			selectedMessages.clear()
		} else {
			selectedMessages = new Set(messages.map((m) => m.message_id))
		}
		allSelected = !allSelected
		selectedMessages = selectedMessages
	}

	function formatPayload(payload: any): string {
		if (!payload) return ''

		try {
			const truncated = JSON.stringify(payload, null, 2)
			return truncated.length > 200 ? truncated.substring(0, 200) + '...' : truncated
		} catch {
			return String(payload).substring(0, 200)
		}
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleString()
	}

	function clearFilters() {
		filterType = ''
		filterMailboxId = ''
		filterMessageId = ''
		currentPage = 1
		refreshMessages()
	}

	function applyFilters() {
		currentPage = 1
		refreshMessages()
	}

	// Exported functions for parent component control
	export function openModal() {
		open = true
		refreshMessages()
	}

	export function closeModal() {
		open = false
	}

	export function toggleModal() {
		if (open) {
			closeModal()
		} else {
			openModal()
		}
	}
</script>

{#if $superadmin}
	<Modal2 bind:isOpen={open} title="Mailbox" target="#content" fixedSize="lg">
		<svelte:fragment slot="header-left">
			<Notification notificationCount={unreadCount} notificationLimit={9999} />
		</svelte:fragment>

		<div class="h-full flex flex-col gap-4">
			<!-- Filters -->
			<div class="border rounded-md p-4 bg-surface-secondary">
				<div class="flex items-center gap-2 mb-3">
					<Filter size="16" />
					<span class="font-medium text-sm">Filters</span>
				</div>

				<div class="flex gap-3">
					<div>
						<label class="block text-xs font-medium mb-1">Type</label>
						<select
							bind:value={filterType}
							class="w-full text-sm border border-gray-200 dark:border-gray-700 rounded px-2 py-1 bg-surface"
						>
							<option value="">All Types</option>
							<option value="trigger">Trigger</option>
							<option value="debouncing_stale_data">Debouncing Stale Data</option>
						</select>
					</div>

					<div>
						<label class="block text-xs font-medium mb-1">Mailbox ID</label>
						<input
							type="text"
							bind:value={filterMailboxId}
							placeholder="e.g., trigger path"
							class="w-full text-sm border border-gray-200 dark:border-gray-700 rounded px-2 py-1 bg-surface"
						/>
					</div>
				</div>

				<div class="flex gap-2 mt-3">
					<Button size="xs" onclick={applyFilters}>
						<Search size="14" />
						Apply
					</Button>
					<Button size="xs" variant="border" onclick={clearFilters}>Clear</Button>
				</div>
			</div>

			<!-- Actions Bar -->
			{#if selectedMessages.size > 0}
				<div
					class="flex items-center gap-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded border"
					transition:fade
				>
					<span class="text-sm font-medium text-blue-700 dark:text-blue-300">
						{selectedMessages.size} message{selectedMessages.size !== 1 ? 's' : ''} selected
					</span>
					<Button size="xs" color="red" onclick={bulkDelete}>
						<Trash2 size="12" />
						Delete Selected
					</Button>
				</div>
			{/if}

			<!-- Messages Table -->
			<div class="flex-1 overflow-hidden border rounded-md">
				{#if loading}
					<div class="p-4 space-y-3">
						{#each Array(5) as _}
							<Skeleton />
						{/each}
					</div>
				{:else if messages.length === 0}
					<div class="p-8 text-center text-secondary">
						<Mailbox size="48" class="mx-auto mb-3 text-tertiary" />
						<h3 class="font-medium mb-1">No messages</h3>
						<p class="text-sm text-tertiary">No mailbox messages found with current filters.</p>
					</div>
				{:else}
					<div class="overflow-auto h-full">
						<table class="w-full">
							<thead class="bg-surface-secondary border-b sticky top-0">
								<tr>
									<th class="text-left p-3 w-12">
										<input
											type="checkbox"
											bind:checked={allSelected}
											onchange={toggleAllSelection}
											class="rounded border-gray-300"
										/>
									</th>
									{#each columns as column}
										<th class="text-left p-3 text-xs font-medium text-secondary {column.class}">
											{column.header}
										</th>
									{/each}
								</tr>
							</thead>
							<tbody>
								{#each messages as message (message.message_id)}
									<tr class="border-b hover:bg-surface-hover">
										<td class="p-3">
											<input
												type="checkbox"
												checked={selectedMessages.has(message.message_id)}
												onchange={() => toggleMessageSelection(message.message_id)}
												class="rounded border-gray-300"
											/>
										</td>
										<td class="p-3 text-sm font-mono">
											{message.message_id}
										</td>
										<td class="p-3 text-sm">
											<span
												class="px-2 py-1 rounded text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
											>
												{message.type}
											</span>
										</td>
										<td class="p-3 text-sm font-mono text-tertiary">
											{message.mailbox_id || '—'}
										</td>
										<td class="p-3 text-sm text-tertiary">
											{formatDate(message.created_at)}
										</td>
										<td class="p-3 text-xs">
											<pre
												class="text-tertiary whitespace-pre-wrap font-mono max-h-20 overflow-y-auto"
												>{formatPayload(message.payload)}</pre
											>
										</td>
										<td class="p-3">
											<List horizontal>
												{#if message.type === 'trigger'}
													<Button
														size="xs2"
														color="blue"
														onclick={() => handleMessage(message.message_id)}
														title="Execute the trigger's runnable"
													>
														<Play size="12" />
													</Button>
												{/if}
												<Button
													size="xs2"
													color="red"
													onclick={() => deleteMessage(message.message_id)}
													title="Delete message"
												>
													<Trash2 size="12" />
												</Button>
											</List>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}
			</div>

			<!-- Pagination -->
			{#if messages.length > 0}
				<div class="flex items-center justify-between p-2 border-t bg-surface-secondary text-sm">
					<span class="text-tertiary">
						Showing {messages.length} message{messages.length !== 1 ? 's' : ''} (Page {currentPage})
					</span>
					<div class="flex gap-2">
						<Button
							size="xs"
							variant="border"
							disabled={currentPage === 1}
							onclick={() => {
								currentPage--
								refreshMessages()
							}}
						>
							Previous
						</Button>
						<Button
							size="xs"
							variant="border"
							disabled={!hasMore}
							onclick={() => {
								currentPage++
								refreshMessages()
							}}
						>
							Next
						</Button>
					</div>
				</div>
			{/if}
		</div>
	</Modal2>
{/if}
