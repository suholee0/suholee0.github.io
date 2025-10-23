const { Client } = require('@notionhq/client');
const { NotionToMarkdown } = require('notion-to-md');
const fs = require('fs').promises;
const path = require('path');
const https = require('https');

// Notion 클라이언트 초기화
// 2025-09-03 API 업데이트: 현재는 안정적인 버전 사용, 추후 SDK v5 업데이트 필요
const notion = new Client({
  auth: process.env.NOTION_API_KEY,
  notionVersion: '2022-06-28' // 안정적인 버전 사용
});
const n2m = new NotionToMarkdown({ notionClient: notion });

// 설정
const DATABASE_ID = process.env.NOTION_DATABASE_ID;
const POSTS_DIR = '_posts';
const IMAGES_DIR = 'assets/img/posts';

// 이미지 다운로드 함수
function downloadImage(url, filepath) {
  return new Promise((resolve, reject) => {
    const file = require('fs').createWriteStream(filepath);
    https.get(url, (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve(filepath);
      });
    }).on('error', (err) => {
      require('fs').unlink(filepath, () => {});
      reject(err);
    });
  });
}

// 날짜 포맷 함수
function formatDate(date) {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// 슬러그 생성 함수
function createSlug(title) {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9가-힣]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .substring(0, 50); // 너무 긴 슬러그 방지
}

// Notion 페이지를 Jekyll 포스트로 변환
async function convertPageToPost(page) {
  try {
    const properties = page.properties;

    // 메타데이터 추출
    const title = properties.Title?.title[0]?.plain_text ||
                 properties.Name?.title[0]?.plain_text ||
                 properties['이름']?.title[0]?.plain_text ||
                 'Untitled';

    const date = properties.Date?.date?.start ||
                properties['날짜']?.date?.start ||
                new Date().toISOString();

    const categories = [];
    if (properties.Category?.select) {
      categories.push(properties.Category.select.name);
    } else if (properties['카테고리']?.select) {
      categories.push(properties['카테고리'].select.name);
    }
    if (categories.length === 0) categories.push('Uncategorized');

    const tags = properties.Tags?.multi_select?.map(tag => tag.name) ||
                properties['태그']?.multi_select?.map(tag => tag.name) ||
                [];

    const published = properties.Published?.checkbox ||
                     properties['게시']?.checkbox ||
                     false;

    // Published가 false면 건너뛰기
    if (!published) {
      console.log(`⏭️  Skipping draft: ${title}`);
      return null;
    }

    console.log(`📝 Processing: ${title}`);

    // Notion 페이지 내용을 Markdown으로 변환
    const mdblocks = await n2m.pageToMarkdown(page.id);
    let mdString = n2m.toMarkdownString(mdblocks).parent || '';

    // 이미지 처리
    const year = new Date().getFullYear();
    const imageDir = path.join(IMAGES_DIR, year.toString());
    await fs.mkdir(imageDir, { recursive: true });

    let imageCounter = 1;
    const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
    const imageMatches = [...mdString.matchAll(imageRegex)];

    for (const match of imageMatches) {
      const [fullMatch, altText, imageUrl] = match;

      if (imageUrl.startsWith('http')) {
        const slug = createSlug(title);
        const ext = path.extname(imageUrl.split('?')[0]) || '.png';
        const filename = `${slug}-${imageCounter++}${ext}`;
        const filepath = path.join(imageDir, filename);

        try {
          await downloadImage(imageUrl, filepath);
          const newImagePath = `/${filepath}`;
          mdString = mdString.replace(fullMatch,
            `![${altText}](${newImagePath}){: width="700" .shadow }`);
          console.log(`  ✅ Downloaded image: ${filename}`);
        } catch (err) {
          console.log(`  ⚠️  Failed to download image: ${imageUrl}`);
        }
      }
    }

    // Front Matter 생성
    const frontMatter = `---
title: "${title.replace(/"/g, '\\"')}"
date: ${formatDate(date)} 00:00:00 +0900
categories: [${categories.join(', ')}]
tags: [${tags.join(', ')}]
math: true
mermaid: true
---

`;

    // 파일명 생성
    const slug = createSlug(title);
    const filename = `${formatDate(date)}-${slug}.md`;
    const filepath = path.join(POSTS_DIR, filename);

    // 파일 저장
    await fs.writeFile(filepath, frontMatter + mdString);
    console.log(`  ✅ Created: ${filename}`);

    return filename;
  } catch (error) {
    console.error(`  ❌ Error processing page: ${error.message}`);
    return null;
  }
}

// 메인 함수
async function main() {
  try {
    console.log('🚀 Starting Notion to Jekyll sync...\n');

    // API 키와 Database ID 확인
    if (!process.env.NOTION_API_KEY || !process.env.NOTION_DATABASE_ID) {
      throw new Error('NOTION_API_KEY and NOTION_DATABASE_ID must be set');
    }

    // Notion 데이터베이스에서 페이지 가져오기
    const response = await notion.databases.query({
      database_id: DATABASE_ID,
      filter: {
        or: [
          {
            property: 'Published',
            checkbox: { equals: true }
          },
          {
            property: '게시',
            checkbox: { equals: true }
          }
        ]
      }
    });

    console.log(`📊 Found ${response.results.length} published posts\n`);

    // 각 페이지를 Jekyll 포스트로 변환
    const posts = [];
    for (const page of response.results) {
      const post = await convertPageToPost(page);
      if (post) posts.push(post);
    }

    console.log(`\n✨ Successfully synced ${posts.length} posts from Notion`);

  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.code === 'object_not_found') {
      console.error('   → Check if Database ID is correct');
      console.error('   → Check if Integration is connected to the database');
    } else if (error.code === 'unauthorized') {
      console.error('   → Check if API Key is correct');
    }
    process.exit(1);
  }
}

main();