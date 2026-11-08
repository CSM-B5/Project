// New file: src/components/StudyResult.jsx
// Shows one MRI study: classification, segmentation images, scores and report.

const STATUS_STYLE = {
  Approved: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  Pending: 'bg-amber-50 text-amber-700 border-amber-200',
};

function ImageBox({ title, src }) {
  return (
    <div>
      <p className="text-xs font-medium text-slate-500 mb-2">{title}</p>
      <div className="bg-black rounded-lg overflow-hidden aspect-square flex items-center justify-center">
        {src ? (
          <img src={src} alt={title} className="w-full h-full object-contain" />
        ) : (
          <span className="text-xs text-slate-400">No image</span>
        )}
      </div>
    </div>
  );
}

export default function StudyResult({ study }) {
  const { patientInfo, classification, segmentation, report } = study;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-semibold text-lg text-slate-900">{patientInfo.caseId}</h3>
          <p className="text-sm text-slate-500">
            {patientInfo.scanType} · {patientInfo.name} · uploaded by {study.radiologistName}
          </p>
        </div>
        <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${STATUS_STYLE[report.status] || ''}`}>
          Report: {report.status}
        </span>
      </div>

      {!study.resultsVisible ? (
        <div className="bg-slate-50 border rounded-lg p-5 text-sm text-slate-600">
          The AI results for this scan will be shown here after your doctor approves the report.
        </div>
      ) : (
        <>
          <div>
            <p className="text-sm text-slate-500">Predicted class</p>
            <p className="text-2xl font-bold text-slate-900">{classification.predictedClass}</p>
            <div className="mt-4 space-y-2">
              {Object.entries(classification.probabilities || {})
                .sort((a, b) => b[1] - a[1])
                .map(([label, value]) => (
                  <div key={label}>
                    <div className="flex justify-between text-sm">
                      <span>{label}</span>
                      <span className="font-mono">{value}%</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-teal-500 rounded-full" style={{ width: `${value}%` }} />
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <div>
            <p className="text-sm text-slate-500 mb-3">Segmentation: {segmentation.status}</p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <ImageBox title="Original MRI" src={segmentation.originalImage} />
              <ImageBox title="Predicted mask" src={segmentation.predictedMask} />
              <ImageBox title="Overlay" src={segmentation.overlayImage} />
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 text-sm">
              <Metric label="Regions" value={segmentation.detectedRegionsCount} />
              <Metric label="Tumor area" value={segmentation.tumorAreaPercent != null ? `${segmentation.tumorAreaPercent}%` : null} />
              <Metric label="Dice score" value={segmentation.diceScore} />
              <Metric label="IoU score" value={segmentation.iouScore} />
            </div>
            {segmentation.diceScore == null && (
              <p className="text-xs text-slate-400 mt-2">
                Dice / IoU appear only when a ground-truth mask is uploaded with the scan.
              </p>
            )}
          </div>

          <div>
            <p className="text-sm text-slate-500 mb-1">Report</p>
            <p className="text-sm text-slate-800 whitespace-pre-line bg-slate-50 border rounded-lg p-4">{report.summary}</p>
            {report.approvedBy && <p className="text-xs text-slate-400 mt-2">Approved by {report.approvedBy}</p>}
          </div>

          <p className="text-xs text-slate-400">{study.disclaimer}</p>
        </>
      )}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="bg-slate-50 rounded-lg p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="font-semibold">{value ?? '—'}</p>
    </div>
  );
}
