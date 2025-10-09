from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from blog_articles.blog.models import Article, Comment
from .serializers import ArticleSerializer, CommentSerializer

class ArticleListAPI(APIView):
    def get_permissions(self):
        if self.request.method == 'GET' and self.request.user.is_superuser:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        if request.user.is_superuser:
            articles = Article.objects.all()
        else:
            articles = Article.objects.filter(author=request.user)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleDetailAPI(APIView):
    def get_permissions(self):
        if self.request.method == 'GET' and self.request.user.is_superuser:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request, id):
        try:
            if request.user.is_superuser:
                article = Article.objects.get(id=id)
            else:
                article = Article.objects.get(id=id, author=request.user)
            serializer = ArticleSerializer(article)
            return Response(serializer.data)
        except Article.DoesNotExist:
            return Response({'error': 'Article non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        try:
            article = Article.objects.get(id=id, author=request.user)
            serializer = ArticleSerializer(article, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Article.DoesNotExist:
            return Response({'error': 'Article non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            article = Article.objects.get(id=id, author=request.user)
            article.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Article.DoesNotExist:
            return Response({'error': 'Article non trouvé'}, status=status.HTTP_404_NOT_FOUND)

class CommentListAPI(APIView):
    def get_permissions(self):
        if self.request.method == 'GET' and self.request.user.is_superuser:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        if request.user.is_superuser:
            comments = Comment.objects.all()
        else:
            comments = Comment.objects.filter(author=request.user)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDetailAPI(APIView):
    def get_permissions(self):
        if self.request.method == 'GET' and self.request.user.is_superuser:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request, id):
        try:
            if request.user.is_superuser:
                comment = Comment.objects.get(id=id)
            else:
                comment = Comment.objects.get(id=id, author=request.user)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response({'error': 'Commentaire non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        try:
            comment = Comment.objects.get(id=id, author=request.user)
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({'error': 'Commentaire non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            comment = Comment.objects.get(id=id, author=request.user)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({'error': 'Commentaire non trouvé'}, status=status.HTTP_404_NOT_FOUND)