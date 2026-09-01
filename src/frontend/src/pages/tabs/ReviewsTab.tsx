import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useOutletContext, useParams } from 'react-router'
import { CircleAlert, LoaderCircle, Star, PencilLine, MessageSquareHeart } from 'lucide-react'

import { reviewsApi, workspacesApi, type PlaceReview, type Workspace } from '@/lib/api'
import { useAuth } from '@/auth'

export function ReviewsTab() {
  const { workspace } = useOutletContext<{ workspace: Workspace }>()
  const { workspaceId = '' } = useParams()
  const { user } = useAuth()
  
  const [reviews, setReviews] = useState<PlaceReview[]>([])
  const [itineraryLocations, setItineraryLocations] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  
  const [locationName, setLocationName] = useState('')
  const [rating, setRating] = useState(5)
  const [reviewText, setReviewText] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const loadData = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const [fetchedReviews, itinerary] = await Promise.all([
        reviewsApi.listReviews(workspaceId),
        workspacesApi.getItinerary(workspaceId)
      ])
      
      setReviews(fetchedReviews)

      // Extract unique location names from itinerary activities
      const locations = new Set<string>()
      itinerary.days.forEach(day => {
        day.activities.forEach(activity => {
          if (activity.location_name && activity.location_name.trim() !== '') {
            locations.add(activity.location_name.trim())
          }
        })
      })
      setItineraryLocations(Array.from(locations).sort())

    } catch (e) {
      setError('Could not load reviews or itinerary.')
    } finally {
      setIsLoading(false)
    }
  }, [workspaceId])

  useEffect(() => { void loadData() }, [loadData])

  // Auto-populate when locationName changes
  useEffect(() => {
    if (!locationName) return
    const existingReview = reviews.find(
      r => r.place_name === locationName && String(r.user_id) === String(user?.id)
    )
    if (existingReview) {
      setRating(existingReview.rating)
      setReviewText(existingReview.comment || '')
    } else {
      setRating(5)
      setReviewText('')
    }
  }, [locationName, reviews, user?.id])

  async function submitReview(e: FormEvent) {
    e.preventDefault()
    if (!locationName.trim()) return
    setIsSubmitting(true)
    setError('')
    try {
      const added = await reviewsApi.submitReview(workspaceId, { 
        place_name: locationName.trim(), 
        rating, 
        comment: reviewText.trim() || undefined 
      })
      
      setReviews(prev => {
        const idx = prev.findIndex(r => String(r.id) === String(added.id) || (r.place_name === added.place_name && String(r.user_id) === String(added.user_id)))
        if (idx >= 0) {
          const next = [...prev]
          next[idx] = added
          return next
        }
        return [added, ...prev]
      })
      
      setLocationName('')
      setRating(5)
      setReviewText('')
    } catch (e) {
      setError('Could not submit review.')
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleEditClick(review: PlaceReview) {
    setLocationName(review.place_name)
    // The useEffect will automatically populate the rest
  }

  const isEditing = reviews.some(r => r.place_name === locationName && String(r.user_id) === String(user?.id))

  if (isLoading) return <section className="workspace-loading"><LoaderCircle className="spin" aria-hidden="true" /><p>Loading reviews…</p></section>

  return (
    <div className="workspace-view">
      <style>{`
        .bento-card {
          background: var(--color-surface);
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
          border: 1px solid var(--color-border);
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .bento-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
        }
        .bento-input {
          padding: 0.65rem 0.75rem;
          border-radius: 0.5rem;
          border: 1px solid var(--color-border);
          background-color: var(--color-surface-dim);
          transition: box-shadow 0.2s ease, border-color 0.2s ease;
          font-family: inherit;
          font-size: 0.95rem;
          color: var(--color-text);
        }
        .bento-input:focus {
          outline: none;
          box-shadow: 0 0 0 2px var(--color-brand);
          border-color: transparent;
        }
        .bento-sidebar {
          background: var(--color-surface);
          padding: 1.75rem;
          border-radius: 1rem;
          height: fit-content;
          position: sticky;
          top: 2rem;
          box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.05);
          border: 1px solid var(--color-border);
        }
        .avatar-circle {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--color-brand) 0%, #a855f7 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 0.9rem;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .edit-btn {
          opacity: 0.4;
          transition: opacity 0.2s ease, color 0.2s ease;
          cursor: pointer;
        }
        .edit-btn:hover {
          opacity: 1;
          color: var(--color-brand);
        }
      `}</style>

      <header className="workspace-view-header">
        <div>
          <h2>Place Ratings & Reviews</h2>
          <p>Rate the places you've visited on this trip</p>
        </div>
      </header>
      
      {error && <div className="inline-error" role="alert"><CircleAlert aria-hidden="true" /><span>{error}</span></div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2.5rem', marginTop: '2rem' }}>
        <div className="reviews-list">
          {reviews.length === 0 ? (
            <div className="reviews-list-empty" style={{ textAlign: 'center', padding: '4rem 2rem', background: 'var(--color-surface-dim)', borderRadius: '1rem', border: '2px dashed var(--color-border)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
              <MessageSquareHeart size={48} color="var(--color-text-dim)" strokeWidth={1.5} />
              <div style={{ maxWidth: '300px' }}>
                <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--color-text)', fontSize: '1.25rem' }}>No reviews yet</h3>
                <p style={{ margin: 0, color: 'var(--color-text-dim)', fontSize: '0.95rem' }}>Share your experience about the places you visited to help others.</p>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {reviews.map(review => (
                <div key={review.id} className="bento-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 600 }}>{review.place_name}</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ display: 'flex', color: '#eab308' }}>
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} size={16} fill={i < review.rating ? 'currentColor' : 'none'} />
                        ))}
                      </div>
                      {String(review.user_id) === String(user?.id) && (
                        <button type="button" onClick={() => handleEditClick(review)} className="recovery-link edit-btn" style={{ fontSize: '0.85rem', padding: 0 }} title="Edit Review">
                          <PencilLine size={18} />
                        </button>
                      )}
                    </div>
                  </div>
                  <p style={{ margin: '0 0 1.25rem 0', fontSize: '0.95rem', color: 'var(--color-text)', lineHeight: 1.6 }}>{review.comment}</p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.85rem', color: 'var(--color-text-dim)' }}>
                    <div className="avatar-circle">
                      {review.user_full_name?.charAt(0).toUpperCase() || review.user_email?.charAt(0).toUpperCase() || '?'}
                    </div>
                    <span style={{ fontWeight: 500, color: 'var(--color-text)' }}>{review.user_full_name || 'Member'}</span>
                    <span>·</span>
                    <time>{new Date(review.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</time>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <aside className="bento-sidebar">
          <h3 style={{ margin: '0 0 1.5rem 0', fontSize: '1.25rem', fontWeight: 600 }}>{isEditing ? 'Update your review' : 'Add a Review'}</h3>
          <form onSubmit={submitReview} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <label style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 500 }}>
              Place Name
              <select className="bento-input" value={locationName} onChange={e => setLocationName(e.target.value)} required>
                <option value="" disabled>Select a location</option>
                {itineraryLocations.map(loc => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
            </label>
            <label style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 500 }}>
              Rating
              <select className="bento-input" value={rating} onChange={e => setRating(Number(e.target.value))}>
                <option value="5">5 Stars - Excellent</option>
                <option value="4">4 Stars - Good</option>
                <option value="3">3 Stars - Average</option>
                <option value="2">2 Stars - Poor</option>
                <option value="1">1 Star - Terrible</option>
              </select>
            </label>
            <label style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 500 }}>
              Review
              <textarea className="bento-input" value={reviewText} onChange={e => setReviewText(e.target.value)} placeholder="Share your experience..." rows={4} style={{ resize: 'vertical' }} />
            </label>
            <button className="button button-primary" type="submit" disabled={isSubmitting || !locationName.trim()} style={{ marginTop: '0.5rem', padding: '0.75rem', borderRadius: '0.5rem' }}>
              {isSubmitting ? <LoaderCircle className="spin" aria-hidden="true" /> : <Star aria-hidden="true" size={18} />} {isEditing ? 'Update Review' : 'Post Review'}
            </button>
          </form>
        </aside>
      </div>
    </div>
  )
}
