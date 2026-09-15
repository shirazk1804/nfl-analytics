import {
  useEffect,
  useState
} from "react"
import "./App.css"
const API_URL = import.meta.env.VITE_API_URL

const teamInfo = {
  ARI: { name: "Arizona Cardinals", logo: "ari" },
  ATL: { name: "Atlanta Falcons", logo: "atl" },
  BAL: { name: "Baltimore Ravens", logo: "bal" },
  BUF: { name: "Buffalo Bills", logo: "buf" },
  CAR: { name: "Carolina Panthers", logo: "car" },
  CHI: { name: "Chicago Bears", logo: "chi" },
  CIN: { name: "Cincinnati Bengals", logo: "cin" },
  CLE: { name: "Cleveland Browns", logo: "cle" },
  DAL: { name: "Dallas Cowboys", logo: "dal" },
  DEN: { name: "Denver Broncos", logo: "den" },
  DET: { name: "Detroit Lions", logo: "det" },
  GB: { name: "Green Bay Packers", logo: "gb" },
  HOU: { name: "Houston Texans", logo: "hou" },
  IND: { name: "Indianapolis Colts", logo: "ind" },
  JAX: { name: "Jacksonville Jaguars", logo: "jax" },
  KC: { name: "Kansas City Chiefs", logo: "kc" },
  LA: { name: "Los Angeles Rams", logo: "lar" },
  LAC: { name: "Los Angeles Chargers", logo: "lac" },
  LV: { name: "Las Vegas Raiders", logo: "lv" },
  MIA: { name: "Miami Dolphins", logo: "mia" },
  MIN: { name: "Minnesota Vikings", logo: "min" },
  NE: { name: "New England Patriots", logo: "ne" },
  NO: { name: "New Orleans Saints", logo: "no" },
  NYG: { name: "New York Giants", logo: "nyg" },
  NYJ: { name: "New York Jets", logo: "nyj" },
  PHI: { name: "Philadelphia Eagles", logo: "phi" },
  PIT: { name: "Pittsburgh Steelers", logo: "pit" },
  SEA: { name: "Seattle Seahawks", logo: "sea" },
  SF: { name: "San Francisco 49ers", logo: "sf" },
  TB: { name: "Tampa Bay Buccaneers", logo: "tb" },
  TEN: { name: "Tennessee Titans", logo: "ten" },
  WAS: { name: "Washington Commanders", logo: "wsh" }
}


function getTeamLogo(team) {

  const logoCode =
    teamInfo[team]?.logo

  return (
    `https://a.espncdn.com/i/teamlogos/nfl/500/${logoCode}.png`
  )
}

function getStatClass(
  value,
  opponentValue,
  lowerIsBetter = false
) {

  if (value === opponentValue) {
    return "stat-value"
  }

  const isBetter = lowerIsBetter
    ? value < opponentValue
    : value > opponentValue

  return isBetter
    ? "stat-value better-stat"
    : "stat-value"
}

function App() {

  const [week, setWeek] = useState(null)
  const [season, setSeason] = useState(2026)

  const [games, setGames] = useState([])
  const [selectedGame, setSelectedGame] = useState("")

  const [prediction, setPrediction] = useState(null)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [gamesLoading, setGamesLoading] = useState(true)
  const [matchupStats, setMatchupStats] = useState(null)

  const currentGame = (
    games.length > 0 &&
    selectedGame !== ""
  )
    ? games[Number(selectedGame)]
    : null

  useEffect(() => {

    async function loadCurrentWeek() {

      try {

        const response = await fetch(
          `${API_URL}/current-week/${season}`
        )

        if (!response.ok) {
          throw new Error(
            "Could not determine current week"
          )
        }

        const data = await response.json()

        setWeek(
          Number(data.week)
        )

      } catch (error) {

        console.error(
          "Current week error:",
          error
        )

        setWeek(1)
      }
    }

    loadCurrentWeek()

  }, [season])

  useEffect(() => {

    async function loadGames() {

      if (week === null) {
        return
      }

      setError("")
      setPrediction(null)
      setGamesLoading(true)

      try {

        const response = await fetch(
          `${API_URL}/games/${season}/${week}`
        )

        if (!response.ok) {

          const data = await response.json()

          throw new Error(
            data.detail ||
            "Could not load games"
          )
        }

        const data = await response.json()

        setGames(data.games)

        if (data.games.length > 0) {
          setSelectedGame("0")
        }

      } catch (error) {

        setGames([])
        setSelectedGame("")

        setError(
          "Could not load games. The backend may still be waking up. Try refreshing in a few seconds."
        )

      } finally {

        setGamesLoading(false)
      }
    }

    loadGames()

  }, [season, week])

  useEffect(() => {

    async function loadMatchupStats() {

      if (!currentGame) {
        setMatchupStats(null)
        return
      }

      try {

        const response = await fetch(
          `${API_URL}/matchup-stats/${season}/${week}/${currentGame.away_team}/${currentGame.home_team}`
        )

        if (!response.ok) {
          setMatchupStats(null)
          return
        }

        const data = await response.json()

        setMatchupStats(data)

      } catch (error) {

        setMatchupStats(null)
      }
    }

    loadMatchupStats()

  }, [currentGame, season, week])

  async function predictGame() {

    setLoading(true)
    setError("")
    setPrediction(null)

    const game = games[
      Number(selectedGame)
    ]

    if (!game) {

      setError(
        "Please select a game."
      )

      setLoading(false)

      return
    }

    try {

      const response = await fetch(
        `${API_URL}/predict`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            season: season,
            week: Number(week),
            home_team: game.home_team,
            away_team: game.away_team
          })
        }
      )

      const text = await response.text()

      let data = {}

      if (text) {
        data = JSON.parse(text)
      }

      if (!response.ok) {

        throw new Error(
          data.detail ||
          `Prediction failed (${response.status})`
        )
      }

      setPrediction(data)

    } catch (error) {

      setError(error.message)

    } finally {

      setLoading(false)
    }
  }


  return (

    <div className="app">

      <div className="container">

        <header>
          <p className="eyebrow">
            MACHINE LEARNING
          </p>

          <h1>
            NFL Game Predictor
          </h1>

          <p className="subtitle">
            Predict NFL games using historical performance,
            advanced statistics, Elo ratings, and machine learning.
          </p>
        </header>


        <div className="predictor-card">

          <div className="filters-row">

            <div className="week-section">

              <label>
                Season
              </label>

              <select
                value={season}
                onChange={(event) => {

                  setSeason(
                    Number(event.target.value)
                  )

                  setPrediction(null)
                }}
              >

                <option value={2025}>
                  2025
                </option>

                <option value={2026}>
                  2026
                </option>

              </select>

            </div>


            <div className="week-section">

              <label>
                Week
              </label>

              <select
                value={week ?? ""}
                onChange={(event) =>
                  setWeek(event.target.value)
                }
              >

                {Array.from(
                  { length: 18 },
                  (_, index) => index + 1
                ).map((weekNumber) => (

                  <option
                    key={weekNumber}
                    value={weekNumber}
                  >
                    Week {weekNumber}
                  </option>

                ))}

              </select>

            </div>

          </div>


          <div className="game-section">

            <label className="game-label">
              MATCHUP
            </label>

            <select
              value={selectedGame}
              onChange={(event) => {
                setSelectedGame(
                  event.target.value
                )

                setPrediction(null)
              }}
            >

              {games.map(
                (game, index) => (

                  <option
                    key={
                      `${game.away_team}-${game.home_team}`
                    }
                    value={index}
                  >

                    {
                      teamInfo[
                        game.away_team
                      ]?.name
                    }
                    {" @ "}
                    {
                      teamInfo[
                        game.home_team
                      ]?.name
                    }

                  </option>

                )
              )}

            </select>

          </div>

          {
            currentGame && (

              <div className="matchup-card">

                <div className="matchup-team">

                  <span className="side-label">
                    AWAY
                  </span>

                  <img
                    src={getTeamLogo(
                      currentGame.away_team
                    )}
                    alt={
                      teamInfo[
                        currentGame.away_team
                      ]?.name
                    }
                  />

                  <h2>
                    {
                      teamInfo[
                        currentGame.away_team
                      ]?.name
                    }
                  </h2>

                  <strong>
                    {currentGame.away_team}
                  </strong>

                </div>


                <div className="matchup-center">

                  <span>
                    WEEK {week}
                  </span>

                  {
                    currentGame.completed ? (
                      <>
                        <strong>
                          FINAL
                        </strong>

                        <div className="final-score">
                          {currentGame.away_score}
                          {" - "}
                          {currentGame.home_score}
                        </div>
                      </>
                    ) : (
                      <strong>
                        @
                      </strong>
                    )
                  }

                  <small>
                    {currentGame.gameday}
                  </small>

                </div>


                <div className="matchup-team">

                  <span className="side-label">
                    HOME
                  </span>

                  <img
                    src={getTeamLogo(
                      currentGame.home_team
                    )}
                    alt={
                      teamInfo[
                        currentGame.home_team
                      ]?.name
                    }
                  />

                  <h2>
                    {
                      teamInfo[
                        currentGame.home_team
                      ]?.name
                    }
                  </h2>

                  <strong>
                    {currentGame.home_team}
                  </strong>

                </div>

              </div>

            )
          }

          {
            matchupStats && (

              <>
                <div className="stats-context">
                  {matchupStats.stats_season} stats through Week {matchupStats.through_week}
                </div>

                <div className="epa-note">
                  EPA/Play = Expected Points Added per play.
                  Higher offensive EPA is better; lower defensive EPA allowed is better.
                </div>

                <div className="team-stats-card">

                  {/* AWAY TEAM */}
                  <div className="team-stats-column">

                    <div className="team-stats-header">

                      <img
                        className="stats-team-logo"
                        src={getTeamLogo(
                          matchupStats.away.team
                        )}
                        alt={
                          teamInfo[
                            matchupStats.away.team
                          ]?.name
                        }
                      />

                      <div>
                        <h3>
                          {
                            teamInfo[
                              matchupStats.away.team
                            ]?.name
                          }
                        </h3>

                        <div className="team-record">
                          {matchupStats.away.record}
                        </div>
                      </div>

                    </div>


                    <div className="stats-grid">

                      <div className="stats-group">

                        <span className="stats-heading">
                          OFFENSE
                        </span>

                        <p>
                          PPG:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.away.points_per_game,
                              matchupStats.home.points_per_game
                            )}
                          >
                            {matchupStats.away.points_per_game}
                          </span>
                        </p>

                        <p>
                          Yards/Game:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.away.yards_per_game,
                              matchupStats.home.yards_per_game
                            )}
                          >
                            {matchupStats.away.yards_per_game}
                          </span>
                        </p>

                        <p>
                          EPA/Play:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.away.epa_per_play,
                              matchupStats.home.epa_per_play
                            )}
                          >
                            {matchupStats.away.epa_per_play}
                          </span>
                        </p>

                      </div>


                      <div className="stats-group">

                        <span className="stats-heading">
                          DEFENSE
                        </span>

                        <p>
                          PPG Allowed:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.away.points_allowed_per_game,
                              matchupStats.home.points_allowed_per_game,
                              true
                            )}
                          >
                            {matchupStats.away.points_allowed_per_game}
                          </span>
                        </p>

                        <p>
                          Yards/Game Allowed:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.away.yards_allowed_per_game,
                              matchupStats.home.yards_allowed_per_game,
                              true
                            )}
                          >
                            {matchupStats.away.yards_allowed_per_game}
                          </span>
                        </p>

                        <p>
                          EPA/Play Allowed:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.away.epa_allowed_per_play,
                              matchupStats.home.epa_allowed_per_play,
                              true
                            )}
                          >
                            {matchupStats.away.epa_allowed_per_play}
                          </span>
                        </p>

                      </div>

                    </div>

                  </div>


                  {/* HOME TEAM */}
                  <div className="team-stats-column">

                    <div className="team-stats-header">

                      <img
                        className="stats-team-logo"
                        src={getTeamLogo(
                          matchupStats.home.team
                        )}
                        alt={
                          teamInfo[
                            matchupStats.home.team
                          ]?.name
                        }
                      />

                      <div>
                        <h3>
                          {
                            teamInfo[
                              matchupStats.home.team
                            ]?.name
                          }
                        </h3>

                        <div className="team-record">
                          {matchupStats.home.record}
                        </div>
                      </div>

                    </div>


                    <div className="stats-grid">

                      <div className="stats-group">

                        <span className="stats-heading">
                          OFFENSE
                        </span>

                        <p>
                          PPG:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.home.points_per_game,
                              matchupStats.away.points_per_game
                            )}
                          >
                            {matchupStats.home.points_per_game}
                          </span>
                        </p>

                        <p>
                          Yards/Game:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.home.yards_per_game,
                              matchupStats.away.yards_per_game
                            )}
                          >
                            {matchupStats.home.yards_per_game}
                          </span>
                        </p>

                        <p>
                          EPA/Play:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.home.epa_per_play,
                              matchupStats.away.epa_per_play
                            )}
                          >
                            {matchupStats.home.epa_per_play}
                          </span>
                        </p>

                      </div>


                      <div className="stats-group">

                        <span className="stats-heading">
                          DEFENSE
                        </span>

                        <p>
                          PPG Allowed:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.home.points_allowed_per_game,
                              matchupStats.away.points_allowed_per_game,
                              true
                            )}
                          >
                            {matchupStats.home.points_allowed_per_game}
                          </span>
                        </p>

                        <p>
                          Yards/Game Allowed:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.home.yards_allowed_per_game,
                              matchupStats.away.yards_allowed_per_game,
                              true
                            )}
                          >
                            {matchupStats.home.yards_allowed_per_game}
                          </span>
                        </p>

                        <p>
                          EPA/Play Allowed:{" "}
                          <span
                            className={getStatClass(
                              matchupStats.home.epa_allowed_per_play,
                              matchupStats.away.epa_allowed_per_play,
                              true
                            )}
                          >
                            {matchupStats.home.epa_allowed_per_play}
                          </span>
                        </p>

                      </div>

                    </div>

                  </div>

                </div>
              </>

            )
          }


          <button
            className="predict-button"
            onClick={predictGame}
            disabled={
              loading ||
              gamesLoading ||
              !currentGame
            }
          >

            {
              gamesLoading
                ? "Loading Games..."
                : loading
                  ? "Predicting..."
                  : "Predict Game"
            }

          </button>


          {
            error && (

              <div className="error">
                {error}
              </div>

            )
          }


          {
            prediction && (

              <div className="results">

                <p className="result-label">
                  {
                    currentGame?.completed
                      ? "PREGAME PREDICTION"
                      : "PREDICTED WINNER"
                  }
                </p>

                <img
                  className="winner-logo"
                  src={getTeamLogo(
                    prediction.predicted_winner
                  )}
                  alt={
                    teamInfo[
                      prediction.predicted_winner
                    ]?.name
                  }
                />

                <h2 className="winner-name">
                  {
                    teamInfo[
                      prediction.predicted_winner
                    ]?.name
                  }
                </h2>

                <div className="winner-probability">

                  {
                    prediction.predicted_winner ===
                      prediction.home_team
                      ? prediction.home_probability
                      : prediction.away_probability
                  }%

                </div>


                <div className="probability-bars">

                  <div className="probability-row">

                    <div className="probability-header">

                      <span>
                        {
                          teamInfo[
                            prediction.away_team
                          ]?.name
                        }
                      </span>

                      <strong>
                        {
                          prediction.away_probability
                        }%
                      </strong>

                    </div>

                    <div className="bar-track">

                      <div
                        className="bar-fill"
                        style={{
                          width:
                            `${prediction.away_probability}%`
                        }}
                      />

                    </div>

                  </div>


                  <div className="probability-row">

                    <div className="probability-header">

                      <span>
                        {
                          teamInfo[
                            prediction.home_team
                          ]?.name
                        }
                      </span>

                      <strong>
                        {
                          prediction.home_probability
                        }%
                      </strong>

                    </div>

                    <div className="bar-track">

                      <div
                        className="bar-fill"
                        style={{
                          width:
                            `${prediction.home_probability}%`
                        }}
                      />

                    </div>

                    <p className="data-source">
                      Based on {prediction.data_source}
                    </p>

                  </div>

                </div>

              </div>

            )
          }

        </div>

      </div>

    </div>
  )
}


export default App