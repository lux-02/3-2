import { useState, useEffect } from "react";
import styles from "@/styles/Forum.module.css";
import { useRouter } from "next/router";

export default function Forum() {
  const [leakBasePosts, setLeakBasePosts] = useState({});

  const [selectedTag, setSelectedTag] = useState("All");

  const [leakBaseUpdateDate, setLeakBaseUpdateDate] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const [searchKeyword, setSearchKeyword] = useState("");

  const [previewImage, setPreviewImage] = useState("");
  const [isPreviewVisible, setIsPreviewVisible] = useState(false);

  const router = useRouter();

  const navigateToRansomware = () => {
    router.push("/");
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

  const handleTagChange = (event) => {
    setSelectedTag(event.target.value);
  };

  const uniqueTags = Object.values(leakBasePosts)
    .flatMap((post) => post.tag || [])
    .filter((value, index, self) => self.indexOf(value) === index);

  const visiblePosts = () => {
    let filteredPosts = [...Object.entries(leakBasePosts)];

    if (selectedTag !== "All") {
      filteredPosts = filteredPosts.filter(([, postDetails]) =>
        postDetails.tag.includes(selectedTag)
      );
    }

    if (searchKeyword.trim()) {
      filteredPosts = filteredPosts.filter(([, postDetails]) =>
        postDetails["post-title"]
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
    fetch("/json/json_leakbase.json")
      .then((response) => response.json())
      .then((data) => {
        setLeakBasePosts(data.posts);
        setLeakBaseUpdateDate(data.file_created_at);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Error loading Lockbit posts data:", error);
      });
  };

  return (
    <div className={styles.wrap}>
      <div className={`${styles.headerWrap} ${styles.leak} `}>
        <div className={styles.nav}>
          <div className={styles.headerBox}>
            <h1 className={styles.headerTitle}>
              $HARKS - LEAK FORUM MONITORING
            </h1>
            <div className={styles.lastUpdateWrap}>
              <p className={styles.lastUpdate}>
                [LeakBase] {leakBaseUpdateDate}
              </p>
            </div>
          </div>
          <div className={styles.pageBtnWrap}>
            <button className={styles.pageBtn} onClick={navigateToRansomware}>
              RANSOMWARE
            </button>
          </div>
        </div>
        <div className={styles.toolBox}>
          <select
            value={selectedTag}
            onChange={handleTagChange}
            className={`${styles.tagSelect}`}
          >
            <option value="All">All Tags</option>
            {uniqueTags.map((tag, index) => (
              <option key={index} value={tag}>
                {tag}
              </option>
            ))}
          </select>
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
                    onClick={() => updatePostsData("leakbase")}
                    className={styles.updateBtn}
                  >
                    LeakBase Update
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
                  <div className={styles.titleWrap}>
                    <h2 className={styles.title}>
                      {postDetails["post-title"]}
                    </h2>
                  </div>
                  <div className={styles.tagWrap}>
                    <div className={styles.tags}>
                      {postDetails["tag"].map((tag, index) => (
                        <span key={index} className={styles.tag}>
                          {tag}
                        </span>
                      ))}
                    </div>
                    <p className={styles.userDate}>
                      {postDetails["user"]} | {postDetails["date"]}
                    </p>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </div>
      )}
    </div>
  );
}
