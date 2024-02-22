import { useState, useEffect } from "react";
import { useRouter } from "next/router";

import styles from "@/styles/Home.module.css";

export default function Home() {
  const [lockbitPosts, setLockbitPosts] = useState({});
  const [blacksuitPosts, setBlacksuitPosts] = useState({});
  const [alphvPosts, setAlphvPosts] = useState({});

  const [selectedCh, setSelectedCh] = useState("All");

  const [lockBitUpdateDate, setLockBitUpdateDate] = useState("");
  const [blackSuitUpdateDate, setBlackSuitUpdateDate] = useState("");
  const [alphvUpdateDate, setAlphvUpdateDate] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const [showTimerOnly, setShowTimerOnly] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState("");

  const [previewImage, setPreviewImage] = useState("");
  const [isPreviewVisible, setIsPreviewVisible] = useState(false);

  const router = useRouter();

  const navigateToForum = () => {
    router.push("/forum");
  };

  useEffect(() => {
    fetchPostsData();
  }, []);

  const handleImageClick = (imageSrc) => {
    if (previewImage === imageSrc) {
      setIsPreviewVisible(false);
      setPreviewImage("");
    } else {
      setPreviewImage(imageSrc);
      setIsPreviewVisible(true);
    }
  };

  const handleImageLeave = () => {
    setIsPreviewVisible(false);
  };

  const visiblePosts = () => {
    let filteredPosts = [
      ...Object.entries(lockbitPosts),
      ...Object.entries(blacksuitPosts),
      ...Object.entries(alphvPosts),
    ];

    if (selectedCh !== "All") {
      filteredPosts = filteredPosts.filter(
        ([, postDetails]) => postDetails.ch === selectedCh
      );
    }

    if (showTimerOnly) {
      filteredPosts = filteredPosts.filter(
        ([, postDetails]) => postDetails["post_timer"]
      );
    }

    if (searchKeyword.trim()) {
      filteredPosts = filteredPosts.filter(
        ([, postDetails]) =>
          postDetails["post-title"]
            .toLowerCase()
            .includes(searchKeyword.toLowerCase()) ||
          postDetails["post-text"]
            .toLowerCase()
            .includes(searchKeyword.toLowerCase())
      );
    }

    return filteredPosts;
  };

  const updatePostsData = (type) => {
    console.log("Update: ", type);

    setIsLoading(true);
    fetch(`http://localhost:8282/api/update?type=${type}`)
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        fetchPostsData();
        window.location.reload();
      })
      .catch((error) => {
        console.error("Error updating posts data:", error);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const fetchPostsData = () => {
    setIsLoading(true);
    fetch("/json/json_lockbit.json")
      .then((response) => response.json())
      .then((data) => {
        setLockbitPosts(data.posts);
        setLockBitUpdateDate(data.file_created_at);
      })
      .catch((error) => {
        console.error("Error loading Lockbit posts data:", error);
      });

    fetch("/json/json_blacksuit.json")
      .then((response) => response.json())
      .then((data) => {
        setBlacksuitPosts(data.posts);
        setBlackSuitUpdateDate(data.file_created_at);
      })
      .catch((error) => {
        console.error("Error loading BlackSuit posts data:", error);
      })
      .finally(() => {
        setIsLoading(false);
      });

    fetch("/json/json_alphv.json")
      .then((response) => response.json())
      .then((data) => {
        setAlphvPosts(data.posts);
        setAlphvUpdateDate(data.file_created_at);
      })
      .catch((error) => {
        console.error("Error loading ALPHV posts data:", error);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const formatDuration = (duration) => {
    const parts = duration.match(/(\d+D)?(\d+h)?(\d+m)?(\d+s)?/);

    let formatted = "";
    if (parts[1]) formatted += parseInt(parts[1]);
    let res = "";
    formatted.trim() != "" ? (res = "D-" + formatted.trim()) : (res = "D-0");
    return res;
  };

  const handleDropChange = (event) => {
    setSelectedCh(event.target.value);
  };

  return (
    <div className={styles.wrap}>
      <div className={styles.headerWrap}>
        <div className={styles.nav}>
          <div className={styles.headerBox}>
            <h1 className={styles.headerTitle}>
              $HARKS - RANSOMWARE MONITORING
            </h1>
            <div className={styles.lastUpdateWrap}>
              <p className={styles.lastUpdate}>[LockBit] {lockBitUpdateDate}</p>
              <p className={styles.lastUpdate}>
                [BlackSuit] {blackSuitUpdateDate}
              </p>
              <p className={styles.lastUpdate}>[ALPHV] {alphvUpdateDate}</p>
            </div>
          </div>
          <div className={styles.pageBtnWrap}>
            <button className={styles.pageBtn} onClick={navigateToForum}>
              LEAK FORUM
            </button>
          </div>
        </div>
        <div className={styles.toolBox}>
          <select
            value={selectedCh}
            onChange={handleDropChange}
            className={styles.chSelect}
          >
            <option value="All">All</option>
            <option value="LockBit">LockBit</option>
            <option value="BlackSuit">BlackSuit</option>
            <option value="ALPHV">ALPHV</option>
          </select>
          <label className={styles.toggleSwitch}>
            <input
              type="checkbox"
              checked={showTimerOnly}
              onChange={() => setShowTimerOnly(!showTimerOnly)}
            />
            <span className={styles.slider}></span>
          </label>
          <input
            type="text"
            placeholder="키워드 검색.."
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
          />
          <div className={styles.btnArea}>
            {isLoading ? (
              <button disabled className={styles.updateBtn}>
                로딩 중...
              </button>
            ) : (
              <>
                {
                  <button
                    onClick={() => updatePostsData("lockbit")}
                    className={styles.updateBtn}
                  >
                    LockBit Update
                  </button>
                }
                {
                  <button
                    onClick={() => updatePostsData("blacksuit")}
                    className={styles.updateBtn}
                  >
                    BlackSuit Update
                  </button>
                }
                {
                  <button
                    onClick={() => updatePostsData("alphv")}
                    className={styles.updateBtn}
                  >
                    ALPHV Update
                  </button>
                }
              </>
            )}
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className={styles.loading}>로딩 중...</div>
      ) : (
        <div className={styles.boxWrap}>
          {visiblePosts().map(([title, postDetails]) => (
            <li key={title} className={styles.box}>
              <div className={styles.imgBox}>
                <img
                  src={`/capture/${postDetails.ch}/${title.replace(
                    /[^a-zA-Z0-9]/g,
                    ""
                  )}.png`}
                  alt={title}
                  className={styles.postImage}
                  onClick={() =>
                    handleImageClick(
                      `/capture/${postDetails.ch}/${title.replace(
                        /[^a-zA-Z0-9]/g,
                        ""
                      )}.png`
                    )
                  }
                />
              </div>
              {isPreviewVisible && (
                <img
                  src={previewImage}
                  className={`${styles.imagePreview} ${
                    isPreviewVisible ? styles.imagePreviewVisible : ""
                  }`}
                  alt="Preview"
                  onClick={handleImageLeave}
                />
              )}

              <div className={styles.contentWrap}>
                <div className={styles.postContent}>
                  <div className={styles.textWrap}>
                    <div className={styles.titleWrap}>
                      <h2 className={styles.title}>
                        {postDetails["post-title"]}
                      </h2>
                      <span className={styles.timer}>
                        {postDetails["post_timer"]
                          ? formatDuration(postDetails["post_timer"])
                          : ""}
                      </span>
                    </div>
                    <p className={styles.postText}>
                      {postDetails["post-text"]}
                    </p>
                  </div>
                </div>
                <p className={styles.update}>{postDetails.ch}</p>
              </div>
            </li>
          ))}
        </div>
      )}
    </div>
  );
}
