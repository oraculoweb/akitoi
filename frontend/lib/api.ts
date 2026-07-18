/**
 * Akitoi API client.
 *
 * - Free tier (public): profiles for the Link Bio views.
 * - Clubs (management): every call carries the Supabase access token
 *   in Authorization; /verify and the digital card stay public.
 */

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// --- Free tier (Link Bio) types ---

export interface Link {
  title: string
  url: string
  link_type: string
  icon?: string
  is_active?: boolean
  order?: number
}

export interface ProfileTheme {
  primary_color?: string
  background_color?: string
  text_color?: string
  profile_image_url?: string
  logo_url?: string
}

export interface Profile {
  id: string
  name: string
  slug: string
  bio: string
  profile_image_url?: string
  logo_url?: string
  links: Link[]
  theme?: ProfileTheme
  is_published: boolean
  views: number
}

async function parseOrThrow<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      if (body?.detail) detail = String(body.detail)
    } catch {
      /* keep default detail */
    }
    throw new Error(detail)
  }
  return response.json() as Promise<T>
}

export const apiClient = {
  /** Public profile for the Link Bio page. */
  async getProfile(slug: string): Promise<Profile> {
    const data = await parseOrThrow<any>(
      await fetch(`${API_URL}/api/v1/profiles/${slug}`, {
        cache: 'no-store',
      })
    )
    // ProfileView reads images from theme; the API returns them at the
    // top level. Normalize so both shapes work.
    return {
      ...data,
      views: data.view_count ?? data.views ?? 0,
      theme: {
        ...(data.theme || {}),
        profile_image_url:
          data.theme?.profile_image_url ?? data.profile_image_url,
        logo_url: data.theme?.logo_url ?? data.logo_url,
      },
    }
  },

  /** Best-effort analytics; never breaks the page. */
  async trackEvent(
    slug: string,
    event: 'view' | 'click',
    _linkId?: string
  ): Promise<void> {
    if (event !== 'view') return // click tracking lands with analytics v2
    await fetch(`${API_URL}/api/v1/profiles/${slug}/view`, {
      method: 'POST',
    }).catch(() => undefined)
  },
}

// --- Clubs (management, Supabase token required) ---

export type MemberEstado = 'vigente' | 'suspendido' | 'vencido' | 'baja'

export interface ClubMember {
  id: string
  name: string
  email: string | null
  phone: string | null
  role: string
  estado: MemberEstado
  valid_until: string | null
  is_active: boolean
}

export interface Organization {
  id: string
  name: string
  slug: string
  logo_url: string | null
  theme: { primary_color: string }
}

export interface ImportResult {
  id: string
  imported_at: string
  created: number
  updated: number
  deactivated: number
  error_count: number
  errors: { row: number | null; error: string }[]
  filename: string | null
}

export interface MemberCard {
  member_id: string
  member_name: string
  verify_url: string
  qr_svg: string
}

export interface VerifyResult {
  valid: boolean
  status: MemberEstado
  member: { name: string }
  organization: { name: string; logo_url: string | null }
  checked_at: string
}

function authHeaders(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}` }
}

const ORGS = `${API_URL}/api/v1/orgs`

export const clubsApi = {
  listMyOrganizations(token: string): Promise<Organization[]> {
    return fetch(ORGS, { headers: authHeaders(token) }).then((r) =>
      parseOrThrow<Organization[]>(r)
    )
  },

  createOrganization(
    token: string,
    name: string
  ): Promise<Organization> {
    return fetch(ORGS, {
      method: 'POST',
      headers: { ...authHeaders(token), 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, owner_profile_id: 'admin' }),
    }).then((r) => parseOrThrow<Organization>(r))
  },

  listMembers(
    token: string,
    orgId: string,
    includeInactive = false
  ): Promise<ClubMember[]> {
    return fetch(
      `${ORGS}/${orgId}/members?include_inactive=${includeInactive}`,
      { headers: authHeaders(token) }
    ).then((r) => parseOrThrow<ClubMember[]>(r))
  },

  importRoster(
    token: string,
    orgId: string,
    file: File
  ): Promise<ImportResult> {
    const form = new FormData()
    form.append('file', file)
    return fetch(`${ORGS}/${orgId}/roster/import`, {
      method: 'POST',
      headers: authHeaders(token),
      body: form,
    }).then((r) => parseOrThrow<ImportResult>(r))
  },

  async downloadExport(
    token: string,
    orgId: string,
    format: 'csv' | 'xlsx' = 'csv'
  ): Promise<void> {
    const response = await fetch(
      `${ORGS}/${orgId}/roster/export?format=${format}`,
      { headers: authHeaders(token) }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `padron.${format}`
    anchor.click()
    URL.revokeObjectURL(url)
  },

  memberAction(
    token: string,
    orgId: string,
    memberId: string,
    action: 'suspend' | 'reactivate' | 'baja'
  ): Promise<unknown> {
    const url =
      action === 'baja'
        ? `${ORGS}/${orgId}/members/${memberId}`
        : `${ORGS}/${orgId}/members/${memberId}/${action}`
    return fetch(url, {
      method: action === 'baja' ? 'DELETE' : 'POST',
      headers: authHeaders(token),
    }).then((r) => parseOrThrow(r))
  },

  issueCard(
    token: string,
    orgId: string,
    memberId: string
  ): Promise<MemberCard> {
    return fetch(`${ORGS}/${orgId}/members/${memberId}/card`, {
      headers: authHeaders(token),
    }).then((r) => parseOrThrow<MemberCard>(r))
  },

  /** PUBLIC: live verdict for a signed card token (no auth). */
  verify(cardToken: string): Promise<VerifyResult> {
    return fetch(`${API_URL}/verify/${cardToken}?format=json`).then((r) =>
      parseOrThrow<VerifyResult>(r)
    )
  },

  /** PUBLIC: QR image of the verification URL (no auth). */
  verifyQrUrl(cardToken: string): string {
    return `${API_URL}/verify/${cardToken}/qr.svg`
  },
}
