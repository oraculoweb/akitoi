import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import ProfileView from '@/components/ProfileView'
import { apiClient } from '@/lib/api'

interface Props {
  params: {
    slug: string
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const profile = await apiClient.getProfile(params.slug)

    return {
      title: `${profile.name} | Akitoi`,
      description: profile.bio || `Perfil de contacto de ${profile.name}`,
    }
  } catch (error) {
    return {
      title: 'Perfil no encontrado | Akitoi',
    }
  }
}

export default async function ProfilePage({ params }: Props) {
  let profile

  try {
    profile = await apiClient.getProfile(params.slug)
  } catch (error) {
    notFound()
  }

  return <ProfileView profile={profile} />
}
