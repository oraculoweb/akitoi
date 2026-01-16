'use client'

import { useEffect } from 'react'
import { Profile } from '@/lib/api'
import { apiClient } from '@/lib/api'
import LinkButton from './LinkButton'

interface ProfileViewProps {
  profile: Profile
}

export default function ProfileView({ profile }: ProfileViewProps) {
  useEffect(() => {
    // Track page view
    apiClient.trackEvent(profile.slug, 'view').catch(console.error)
  }, [profile.slug])

  const handleLinkClick = async (linkId?: string) => {
    try {
      await apiClient.trackEvent(profile.slug, 'click', linkId)
    } catch (error) {
      console.error('Failed to track click:', error)
    }
  }

  const primaryColor = profile.theme?.primary_color || '#3b82f6'
  const backgroundColor = profile.theme?.background_color || '#ffffff'
  const textColor = profile.theme?.text_color || '#1f2937'

  return (
    <div
      className="min-h-screen py-12 px-4 sm:px-6 lg:px-8"
      style={{ backgroundColor }}
    >
      <div className="max-w-2xl mx-auto">
        {/* Profile Header */}
        <div className="text-center mb-8">
          {/* Profile Image */}
          {profile.theme?.profile_image_url && (
            <div className="mb-6">
              <img
                src={profile.theme.profile_image_url}
                alt={profile.name}
                className="w-32 h-32 rounded-full mx-auto object-cover border-4"
                style={{ borderColor: primaryColor }}
              />
            </div>
          )}

          {/* Logo */}
          {profile.theme?.logo_url && (
            <div className="mb-4">
              <img
                src={profile.theme.logo_url}
                alt={`${profile.name} logo`}
                className="h-16 mx-auto object-contain"
              />
            </div>
          )}

          {/* Name */}
          <h1
            className="text-4xl font-bold mb-3"
            style={{ color: textColor }}
          >
            {profile.name}
          </h1>

          {/* Bio */}
          {profile.bio && (
            <p
              className="text-lg mb-2"
              style={{ color: textColor, opacity: 0.8 }}
            >
              {profile.bio}
            </p>
          )}

          {/* View Count */}
          <p
            className="text-sm"
            style={{ color: textColor, opacity: 0.6 }}
          >
            {profile.views} {profile.views === 1 ? 'visita' : 'visitas'}
          </p>
        </div>

        {/* Links */}
        <div className="space-y-4">
          {profile.links
            .sort((a, b) => (a.order || 0) - (b.order || 0))
            .map((link, index) => (
              <LinkButton
                key={index}
                link={link}
                primaryColor={primaryColor}
                textColor={textColor}
                onClick={() => handleLinkClick()}
              />
            ))}
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <p
            className="text-sm"
            style={{ color: textColor, opacity: 0.5 }}
          >
            Powered by{' '}
            <a
              href="/"
              className="hover:underline font-semibold"
              style={{ color: primaryColor }}
            >
              Akitoi
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
