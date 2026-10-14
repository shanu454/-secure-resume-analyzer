// One block per skill in the job description: filled = found on the resume, outlined = missing.
// Required skills come first at full height; preferred skills follow, shorter.
export default function CoverageStrip({ matched, missing }) {
  const all = [
    ...matched.map((s) => ({ ...s, found: true })),
    ...missing.map((s) => ({ ...s, found: false })),
  ]
  const required = all.filter((s) => s.importance === 'required')
  const preferred = all.filter((s) => s.importance === 'preferred')
  const sort = (list) => [...list].sort((a, b) => Number(b.found) - Number(a.found))

  const count = (list) => `${list.filter((s) => s.found).length} of ${list.length}`

  return (
    <figure className="coverage">
      <div className="strip" role="img" aria-label={`Required skills found: ${count(required)}. Preferred skills found: ${count(preferred)}.`}>
        {sort(required).map((s) => (
          <span key={s.name} className={`seg required ${s.found ? 'found' : 'absent'}`} title={`${s.name}: ${s.found ? 'found' : 'missing'}`} />
        ))}
        {preferred.length > 0 && <span className="gap" />}
        {sort(preferred).map((s) => (
          <span key={s.name} className={`seg preferred ${s.found ? 'found' : 'absent'}`} title={`${s.name}: ${s.found ? 'found' : 'missing'}`} />
        ))}
      </div>
      <figcaption>
        {required.length > 0 && <span>{count(required)} required skills found</span>}
        {preferred.length > 0 && <span>{count(preferred)} nice-to-have skills found</span>}
      </figcaption>
    </figure>
  )
}
