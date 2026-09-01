import { useState } from 'react'
import { useOutletContext, useParams } from 'react-router'
import { CircleAlert, Download, Link as LinkIcon, LoaderCircle, Users } from 'lucide-react'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'

import { itinerariesApi, type Workspace } from '@/lib/api'

export function ShareTab() {
  const { workspace } = useOutletContext<{ workspace: Workspace }>()
  const { workspaceId = '' } = useParams()
  
  const [isExporting, setIsExporting] = useState(false)
  const [exportError, setExportError] = useState('')

  const handleExportPDF = async () => {
    setIsExporting(true)
    setExportError('')
    try {
      // 1. Fetch itinerary data & Font simultaneously
      const [itinerary, fontResponse] = await Promise.all([
        itinerariesApi.getItinerary(workspaceId),
        fetch('/Roboto-Regular.ttf')
      ])
      
      const fontBuffer = await fontResponse.arrayBuffer()
      let binary = ''
      const bytes = new Uint8Array(fontBuffer)
      for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i])
      }
      const fontBase64 = window.btoa(binary)

      // 2. Initialize jsPDF
      const doc = new jsPDF()
      
      // Add Vietnamese-supporting font
      doc.addFileToVFS('Roboto-Regular.ttf', fontBase64)
      doc.addFont('Roboto-Regular.ttf', 'Roboto', 'normal')
      doc.setFont('Roboto')
      
      // 3. Add Document Header
      doc.setFontSize(22)
      doc.text(workspace.title || 'Trip Itinerary', 14, 22)
      
      doc.setFontSize(11)
      doc.setTextColor(100)
      const dateRange = workspace.start_date && workspace.end_date 
        ? `${workspace.start_date} to ${workspace.end_date}` 
        : 'Dates TBD'
      doc.text(`Destination: ${workspace.destination || 'TBD'} | ${dateRange}`, 14, 32)
      
      let currentY = 45

      // 4. Add each day to the PDF
      if (!itinerary || !itinerary.days || itinerary.days.length === 0) {
        doc.setFontSize(12)
        doc.text('No itinerary details found for this trip.', 14, currentY)
      } else {
        for (const day of itinerary.days) {
          // Add day header
          doc.setFontSize(16)
          doc.setTextColor(0)
          const dayTitle = `Day ${day.day_index}${day.travel_date ? ` - ${day.travel_date}` : ''}`
          doc.text(dayTitle, 14, currentY)
          
          if (day.title) {
            doc.setFontSize(12)
            doc.setTextColor(100)
            doc.text(day.title, 14, currentY + 6)
            currentY += 12
          } else {
            currentY += 8
          }
          
          if (day.activities && day.activities.length > 0) {
            const tableData = day.activities.map(act => {
              const time = act.start_time && act.end_time 
                ? `${act.start_time.substring(0, 5)} - ${act.end_time.substring(0, 5)}`
                : act.start_time ? act.start_time.substring(0, 5) : 'Anytime'
              
              return [
                time,
                act.title || '',
                act.location_name || '',
                act.notes || ''
              ]
            })

            autoTable(doc, {
              startY: currentY,
              head: [['Time', 'Activity', 'Location', 'Notes']],
              body: tableData,
              theme: 'striped',
              headStyles: { fillColor: [41, 128, 185] },
              margin: { left: 14, right: 14 },
              styles: { font: 'Roboto', fontSize: 10, cellPadding: 4 },
              columnStyles: {
                0: { cellWidth: 35 },
                1: { cellWidth: 50 },
                2: { cellWidth: 50 }
              }
            })
            
            // @ts-expect-error jsPDF-autotable adds lastAutoTable to doc
            currentY = doc.lastAutoTable.finalY + 15
          } else {
            doc.setFontSize(10)
            doc.setTextColor(150)
            doc.text('No activities scheduled for this day.', 14, currentY)
            currentY += 15
          }
          
          // Add a new page if getting too close to bottom
          if (currentY > 260) {
            doc.addPage()
            currentY = 20
          }
        }
      }

      // 5. Save the PDF
      doc.save(`Trip_Itinerary_${workspace.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.pdf`)
      
    } catch (e) {
      console.error(e)
      setExportError('Export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="workspace-view">
      <style>{`
        .bento-section {
          background: var(--color-surface);
          border-radius: 1rem;
          padding: 2rem;
          border: 1px solid var(--color-border);
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
          margin-bottom: 2rem;
        }
        .bento-section h3 {
          font-size: 1.25rem;
          margin-bottom: 0.5rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .bento-section p.section-desc {
          color: var(--color-text-dim);
          margin-bottom: 1.5rem;
          font-size: 0.95rem;
        }
        .coming-soon-badge {
          background: var(--color-surface-dim);
          border: 1px solid var(--color-border);
          padding: 0.5rem 1rem;
          border-radius: 9999px;
          display: inline-block;
          font-size: 0.85rem;
          font-weight: 500;
          color: var(--color-text-dim);
        }
      `}</style>

      <header className="workspace-view-header">
        <div>
          <h2>Share & Export</h2>
          <p>Generate shareable links or download your itinerary</p>
        </div>
      </header>

      {exportError && (
        <div className="inline-error" role="alert" style={{ marginBottom: '2rem' }}>
          <CircleAlert aria-hidden="true" />
          <span>{exportError}</span>
        </div>
      )}

      <div style={{ maxWidth: '800px', display: 'grid', gap: '2rem' }}>
        
        {/* Export to PDF Section */}
        <section className="bento-section">
          <h3><Download size={20} className="text-brand" /> Export as PDF</h3>
          <p className="section-desc">Download a beautifully formatted PDF of your itinerary, perfect for printing or viewing offline during your trip.</p>
          
          <button 
            className="button button-primary" 
            type="button" 
            onClick={() => void handleExportPDF()} 
            disabled={isExporting}
            style={{ borderRadius: '9999px', padding: '0.6rem 1.5rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}
          >
            {isExporting ? (
              <><LoaderCircle className="spin" aria-hidden="true" size={18} /> Compiling PDF...</>
            ) : (
              <><Download aria-hidden="true" size={18} /> Export Itinerary</>
            )}
          </button>
        </section>

        {/* Shareable Link Section (Placeholder) */}
        <section className="bento-section">
          <h3><LinkIcon size={20} className="text-brand" /> Shareable Link</h3>
          <p className="section-desc">Generate a secure link to let others view or edit this trip without needing to be manually invited.</p>
          
          <div className="coming-soon-badge">
            Feature coming soon
          </div>
        </section>

      </div>
    </div>
  )
}
