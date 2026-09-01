import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useOutletContext, useParams } from 'react-router'
import { CircleAlert, LoaderCircle, Star } from 'lucide-react'

import { reviewsApi, type PlaceReview, type Workspace } from '@/lib/api'

export function ReviewsTab() {
  const { workspace } = useOutletContext<{ workspace: Workspace }>()
  const { workspaceId = '' } = useParams()
  
  const [reviews, setReviews] = useState<PlaceReview[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  
  const [locationName, setLocationName] = useState('')
  const [rating, setRating] = useState(5)
  const [reviewText, setReviewText] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const loadReviews = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      setReviews(await reviewsApi.listReviews(workspaceId))
    } catch (e) {
      setError('Could not load reviews.')
    } finally {
      setIsLoading(false)
    }
  }, [workspaceId])

  useEffect(() => { void loadReviews() }, [loadReviews])

  async function submitReview(e: FormEvent) {
    e.preventDefault()
    if (!locationName.trim()) return
    setIsSubmitting(true)
    setError('')
    try {
      const added = await reviewsApi.submitReview(workspaceId, { 
        location_name: locationName.trim(), 
        rating, 
        review_text: reviewText.trim() || undefined 
      })
      setReviews([added, ...reviews])
      setLocationName('')
      setRating(5)
      setReviewText('')
    } catch (e) {
      setError('Could not submit review.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) return <section className="workspace-loading"><LoaderCircle className="spin" aria-hidden="true" /><p>Loading reviews…</p></section>

  return (
    <div className="workspace-view">
      <header className="workspace-view-header">
        <div>
          <h2>Place Ratings & Reviews</h2>
          <p>Rate the places you've visited on this trip</p>
        </div>
      </header>
      
      {error && <div className="inline-error" role="alert"><CircleAlert aria-hidden="true" /><span>{error}</span></div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem', marginTop: '2rem' }}>
        <div className="reviews-list">
          {reviews.length === 0 ? (
            <div className="reviews-list-empty" style={{ textAlign: 'center', padding: '3rem', background: 'var(--color-surface-dim)', borderRadius: '0.5rem' }}>
              <p style={{ color: 'var(--color-text-dim)' }}>No reviews yet. Share your experience!</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {reviews.map(review => (
                <div key={review.id} style={{ padding: '1.25rem', background: 'var(--color-surface-dim)', borderRadius: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{review.location_name}</h3>
                    <div style={{ display: 'flex', color: '#eab308' }}>
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} size={16} fill={i < review.rating ? 'currentColor' : 'none'} />
                      ))}
                    </div>
                  </div>
                  <p style={{ margin: '0 0 1rem 0', fontSize: '0.9rem', color: 'var(--color-text)' }}>{review.review_text}</p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--color-text-dim)' }}>
                    <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: 'var(--color-brand)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                      {review.user?.full_name?.charAt(0).toUpperCase() || review.user?.email.charAt(0).toUpperCase()}
                    </div>
                    <span>{review.user?.full_name || 'Member'}</span>
                    <span>·</span>
                    <time>{new Date(review.created_at).toLocaleDateString()}</time>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <aside style={{ background: 'var(--color-surface-dim)', padding: '1.5rem', borderRadius: '0.5rem', height: 'fit-content' }}>
          <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Add a Review</h3>
          <form onSubmit={submitReview} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <label style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.85rem' }}>
              Place Name
              <input value={locationName} onChange={e => setLocationName(e.target.value)} required placeholder="e.g., Louvre Museum" style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--color-border)' }} />
            </label>
            <label style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.85rem' }}>
              Rating
              <select value={rating} onChange={e => setRating(Number(e.target.value))} style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
                <option value="5">5 Stars - Excellent</option>
                <option value="4">4 Stars - Good</option>
                <option value="3">3 Stars - Average</option>
                <option value="2">2 Stars - Poor</option>
                <option value="1">1 Star - Terrible</option>
              </select>
            </label>
            <label style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.85rem' }}>
              Review
              <textarea value={reviewText} onChange={e => setReviewText(e.target.value)} placeholder="How was it?" rows={4} style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--color-border)', resize: 'vertical' }} />
            </label>
            <button className="button button-primary" type="submit" disabled={isSubmitting || !locationName.trim()} style={{ marginTop: '0.5rem' }}>
              {isSubmitting ? <LoaderCircle className="spin" aria-hidden="true" /> : <Star aria-hidden="true" />} Post Review
            </button>
          </form>
        </aside>
      </div>
    </div>
  )
}
