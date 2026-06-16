import { ApiRequestError } from './types'

const BASE = 'http://127.0.0.1:8000'

export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, options)

  if (!res.ok) {
    const envelope = await res.json().catch(() => ({
      error: { code: 'internal_error', message: 'An unexpected error occurred.', details: {} },
    }))
    throw new ApiRequestError(
      res.status,
      envelope.error?.code ?? 'internal_error',
      envelope.error?.message ?? 'An unexpected error occurred.',
      envelope.error?.details ?? {},
    )
  }

  // 204 No Content has no body
  if (res.status === 204) {
    return undefined as T
  }

  const contentType = res.headers.get('content-type') ?? ''
  if (contentType.startsWith('application/json')) {
    return res.json() as Promise<T>
  }
  return res.blob() as Promise<T>
}
